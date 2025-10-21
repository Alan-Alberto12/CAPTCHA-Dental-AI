"""
Dataset Management API Routes

Endpoints for managing Kaggle datasets and processing annotations
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from services.database import get_db
from services.kaggle_service import KaggleDatasetService
from models.dataset import Dataset
from api.routes.auth import get_current_user
from models.user import User


router = APIRouter(prefix="/datasets", tags=["datasets"])


# Pydantic schemas
class DatasetCreate(BaseModel):
    kaggle_path: str
    name: Optional[str] = None
    description: Optional[str] = None


class DatasetResponse(BaseModel):
    id: int
    name: str
    kaggle_path: str
    local_path: Optional[str]
    total_images: int
    total_annotations: int
    is_downloaded: bool
    is_processed: bool

    class Config:
        from_attributes = True


class DatasetStats(BaseModel):
    name: str
    kaggle_path: str
    total_images: int
    total_annotations: int
    is_downloaded: bool
    is_processed: bool
    local_path: Optional[str]


@router.post("/download", response_model=DatasetResponse)
async def download_dataset(
    dataset_create: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download a dataset from Kaggle

    **Example:**
    ```json
    {
        "kaggle_path": "humansintheloop/teeth-segmentation-on-dental-x-ray-images",
        "name": "Teeth Segmentation Dataset"
    }
    ```
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can download datasets"
        )

    kaggle_service = KaggleDatasetService(db)

    try:
        local_path, dataset = kaggle_service.download_teeth_segmentation_dataset(
            kaggle_path=dataset_create.kaggle_path
        )

        # Update name and description if provided
        if dataset_create.name:
            dataset.name = dataset_create.name
        if dataset_create.description:
            dataset.description = dataset_create.description

        db.commit()
        db.refresh(dataset)

        return dataset

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download dataset: {str(e)}"
        )


@router.post("/{dataset_id}/process", response_model=DatasetResponse)
async def process_dataset(
    dataset_id: int,
    annotations_file: str = "annotations.json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process annotations for a downloaded dataset
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can process datasets"
        )

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )

    if not dataset.is_downloaded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset not downloaded yet"
        )

    kaggle_service = KaggleDatasetService(db)

    try:
        processed_count = kaggle_service.process_dataset_annotations(
            dataset=dataset,
            annotations_file=annotations_file
        )

        db.refresh(dataset)

        return dataset

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process dataset: {str(e)}"
        )


@router.get("/", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all datasets
    """
    datasets = db.query(Dataset).offset(skip).limit(limit).all()
    return datasets


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get dataset by ID
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    return dataset


@router.get("/{dataset_id}/stats", response_model=DatasetStats)
async def get_dataset_stats(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get statistics for a dataset
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )

    kaggle_service = KaggleDatasetService(db)
    stats = kaggle_service.get_dataset_stats(dataset)

    return stats


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a dataset (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete datasets"
        )

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )

    db.delete(dataset)
    db.commit()

    return {"message": "Dataset deleted successfully"}
