"""ML API routes — prediction and training endpoints"""
import os
import tempfile
import torch

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.routes.auth import get_current_admin, get_current_user
from ml.config import MODEL_ARCH, ML_MODELS_DIR
from models.user import Image, Prediction, User
from services.database import get_db
from services.s3_service import s3_service

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

# NOTE: /predict/upload must come BEFORE /predict/{image_id} so FastAPI matches it first
@router.post("/predict/upload")
async def predict_uploaded_image(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
):
    #run CNN prediction on an uploaded image (not stored in DB)
    from ml.predict import PredictionService

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type. Use JPEG, PNG, or WEBP.")

    image_bytes = await file.read()

    service = PredictionService.get_instance()
    if service.model is None:
        if not service.load_model():
            raise HTTPException(status_code=503, detail="No trained model available")

    return service.predict(image_bytes)


@router.post("/predict/{image_id}")
def predict_image(
    image_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    #run CNN prediction on an existing image by ID
    from ml.predict import PredictionService

    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        success = s3_service.download_file(image.image_url, tmp_path)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to download image from S3")

        with open(tmp_path, "rb") as f:
            image_bytes = f.read()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    service = PredictionService.get_instance()
    if service.model is None:
        if not service.load_model():
            raise HTTPException(status_code=503, detail="No trained model available")

    result = service.predict(image_bytes)

    prediction = Prediction(
        image_id=image.id,
        model_name=service.arch,
        predicted_label=result["label"],
        confidence=result["confidence"],
        model_version="latest",
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return {
        "prediction_id": prediction.id,
        "image_id": image.id,
        "label": result["label"],
        "confidence": result["confidence"],
        "model": service.arch,
    }


@router.post("/train", status_code=202)
def trigger_training(
    background_tasks: BackgroundTasks,
    arch: str = MODEL_ARCH,
    epochs: int = 20,
    _: User = Depends(get_current_admin),
):
    #trigger model training in the background (admin only)
    from ml.train import train_model

    if arch != "efficientnet_b0":
        raise HTTPException(status_code=400, detail="Invalid architecture")

    background_tasks.add_task(train_model, arch=arch, epochs=epochs)

    return {
        "message": "Training started in background",
        "architecture": arch,
        "epochs": epochs,
    }


@router.get("/model/status")
def model_status(_: User = Depends(get_current_user)):
    #check if a trained model is available and its metadata
    latest = ML_MODELS_DIR / "latest.pth"

    if not latest.exists():
        return {"available": False}

    checkpoint = torch.load(latest, map_location="cpu", weights_only=False)

    return {
        "available": True,
        "architecture": checkpoint.get("arch"),
        "best_val_acc": checkpoint.get("best_val_acc"),
        "trained_at": checkpoint.get("trained_at"),
    }
