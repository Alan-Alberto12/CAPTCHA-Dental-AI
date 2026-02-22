"""
ML API routes — prediction and training endpoints.
"""

import os
import tempfile

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.routes.auth import get_current_admin, get_current_user
from models.user import Image, Prediction, User
from services.database import get_db
from services.s3_service import s3_service
from ml.config import DEFAULT_MODEL_ARCH, NUM_EPOCHS, SUPPORTED_MODEL_ARCHS

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


# NOTE: /predict/upload must come BEFORE /predict/{image_id} so FastAPI matches it first
@router.post("/predict/upload")
async def predict_uploaded_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Run CNN prediction on an uploaded image (not stored in DB)."""
    from ml.predict import PredictionService

    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
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
    current_user: User = Depends(get_current_user),
):
    """Run CNN prediction on an existing image by ID."""
    from ml.predict import PredictionService

    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Download image from S3 to a temp file
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

    # Load model if not already loaded
    service = PredictionService.get_instance()
    if service.model is None:
        if not service.load_model():
            raise HTTPException(status_code=503, detail="No trained model available")

    result = service.predict(image_bytes)

    # Store prediction in DB
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
    arch: str = DEFAULT_MODEL_ARCH,
    epochs: int = NUM_EPOCHS,
    current_user: User = Depends(get_current_admin),
):
    """Trigger model training in the background (admin only)."""
    from ml.train import train_model

    if arch not in SUPPORTED_MODEL_ARCHS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid architecture. Supported: {', '.join(SUPPORTED_MODEL_ARCHS)}",
        )

    background_tasks.add_task(train_model, arch=arch, epochs=epochs)

    return {
        "message": "Training started in background",
        "architecture": arch,
        "epochs": epochs,
    }


@router.get("/model/status")
def model_status(current_user: User = Depends(get_current_user)):
    """Check if a trained model is available and its metadata."""
    from ml.config import ML_MODELS_DIR

    latest = ML_MODELS_DIR / "latest.pth"

    if not latest.exists():
        return {"available": False}

    import torch

    checkpoint = torch.load(latest, map_location="cpu", weights_only=False)

    return {
        "available": True,
        "architecture": checkpoint.get("arch"),
        "best_val_acc": checkpoint.get("best_val_acc"),
        "trained_at": checkpoint.get("trained_at"),
    }
