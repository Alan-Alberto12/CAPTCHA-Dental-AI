"""
Teeth Segmentation Prediction API Routes

Endpoints for running ML predictions on dental X-ray images
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path
import tempfile

from services.database import get_db
from services.segmentation_service import SegmentationService
from models.prediction import Prediction, SegmentationModel
from models.image import Image
from api.routes.auth import get_current_user
from models.user import User


router = APIRouter(prefix="/predictions", tags=["predictions"])


# Pydantic schemas
class PredictionRequest(BaseModel):
    image_id: int
    model_id: Optional[int] = None
    confidence_threshold: float = 0.5


class PredictionResponse(BaseModel):
    id: int
    image_id: int
    model_id: int
    tooth_class: int
    tooth_notation: Optional[str]
    confidence_score: float
    bbox: Optional[List[int]]
    area: Optional[float]
    is_verified: bool
    inference_time: Optional[float]

    class Config:
        from_attributes = True


class PredictionBatchResponse(BaseModel):
    image_id: int
    predictions: List[PredictionResponse]
    total_predictions: int
    inference_time: float


class SegmentationModelResponse(BaseModel):
    id: int
    name: str
    version: str
    architecture: str
    num_classes: int
    is_active: bool
    is_default: bool
    accuracy: Optional[float]
    mean_iou: Optional[float]
    dice_coefficient: Optional[float]

    class Config:
        from_attributes = True


@router.post("/predict", response_model=PredictionBatchResponse)
async def predict_teeth_segmentation(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run teeth segmentation prediction on an image

    **Parameters:**
    - `image_id`: ID of the image to predict
    - `model_id`: ID of the segmentation model (uses default if not specified)
    - `confidence_threshold`: Minimum confidence score (0.0 - 1.0)

    **Returns:**
    - List of predicted teeth with segmentation masks
    """
    # Check image exists and user has access
    image = db.query(Image).filter(Image.id == request.image_id).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Check permissions
    if not current_user.is_admin and image.user_id != current_user.id and not image.dataset_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to predict on this image"
        )

    # Run prediction
    segmentation_service = SegmentationService(db)

    try:
        predictions = segmentation_service.predict(
            image_id=request.image_id,
            model_id=request.model_id,
            user_id=current_user.id,
            confidence_threshold=request.confidence_threshold,
        )

        # Calculate total inference time
        total_inference_time = predictions[0].inference_time if predictions else 0

        return {
            "image_id": request.image_id,
            "predictions": predictions,
            "total_predictions": len(predictions),
            "inference_time": total_inference_time,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/image/{image_id}", response_model=List[PredictionResponse])
async def get_predictions_for_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all predictions for an image
    """
    image = db.query(Image).filter(Image.id == image_id).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Check permissions
    if not current_user.is_admin and image.user_id != current_user.id and not image.dataset_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access predictions for this image"
        )

    predictions = db.query(Prediction).filter(
        Prediction.image_id == image_id
    ).all()

    return predictions


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get prediction by ID
    """
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )

    # Check permissions
    image = prediction.image
    if not current_user.is_admin and image.user_id != current_user.id and not image.dataset_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this prediction"
        )

    return prediction


@router.post("/{prediction_id}/verify")
async def verify_prediction(
    prediction_id: int,
    is_correct: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Verify a prediction (human-in-the-loop feedback)

    **Parameters:**
    - `prediction_id`: ID of the prediction
    - `is_correct`: Whether the prediction is correct
    """
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )

    # Check permissions
    image = prediction.image
    if not current_user.is_admin and image.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this prediction"
        )

    # Update verification status
    prediction.is_verified = is_correct
    prediction.verified_by = current_user.id

    db.commit()
    db.refresh(prediction)

    return {
        "message": "Prediction verified successfully",
        "prediction_id": prediction_id,
        "is_verified": is_correct
    }


@router.get("/{prediction_id}/visualize")
async def visualize_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get visualization of a single prediction
    """
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )

    # Check permissions
    image = prediction.image
    if not current_user.is_admin and image.user_id != current_user.id and not image.dataset_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this prediction"
        )

    # Create visualization
    segmentation_service = SegmentationService(db)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        output_path = temp_file.name

    try:
        segmentation_service.visualize_predictions(
            image_path=image.file_path,
            predictions=[prediction],
            output_path=output_path,
        )

        return FileResponse(
            output_path,
            media_type="image/png",
            filename=f"prediction_{prediction_id}.png"
        )

    except Exception as e:
        if Path(output_path).exists():
            Path(output_path).unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create visualization: {str(e)}"
        )


@router.get("/image/{image_id}/visualize")
async def visualize_all_predictions(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get visualization of all predictions for an image
    """
    image = db.query(Image).filter(Image.id == image_id).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Check permissions
    if not current_user.is_admin and image.user_id != current_user.id and not image.dataset_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this image"
        )

    # Get all predictions
    predictions = db.query(Prediction).filter(
        Prediction.image_id == image_id
    ).all()

    if not predictions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No predictions found for this image"
        )

    # Create visualization
    segmentation_service = SegmentationService(db)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        output_path = temp_file.name

    try:
        segmentation_service.visualize_predictions(
            image_path=image.file_path,
            predictions=predictions,
            output_path=output_path,
        )

        return FileResponse(
            output_path,
            media_type="image/png",
            filename=f"predictions_image_{image_id}.png"
        )

    except Exception as e:
        if Path(output_path).exists():
            Path(output_path).unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create visualization: {str(e)}"
        )


# Model management endpoints
@router.get("/models/", response_model=List[SegmentationModelResponse])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List available segmentation models
    """
    query = db.query(SegmentationModel)

    if active_only:
        query = query.filter(SegmentationModel.is_active == True)

    models = query.offset(skip).limit(limit).all()
    return models


@router.get("/models/{model_id}", response_model=SegmentationModelResponse)
async def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get model by ID
    """
    model = db.query(SegmentationModel).filter(
        SegmentationModel.id == model_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )

    return model
