"""
Image Upload and Management API Routes

Endpoints for uploading dental X-ray images (including DICOM)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path
import shutil
import tempfile

from services.database import get_db
from services.dicom_service import DICOMService
from models.image import Image, ImageType, ImageStatus
from api.routes.auth import get_current_user
from models.user import User


router = APIRouter(prefix="/images", tags=["images"])


# Pydantic schemas
class ImageResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    image_type: str
    status: str
    width: Optional[int]
    height: Optional[int]
    file_size: Optional[int]
    is_annotated: bool
    is_predicted: bool
    annotation_count: int
    patient_id: Optional[str]

    class Config:
        from_attributes = True


class ImageUploadResponse(BaseModel):
    image: ImageResponse
    converted_path: Optional[str]
    message: str


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    image_type: str = Form("panoramic"),
    convert_dicom: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a dental X-ray image (supports DICOM and standard image formats)

    **Supported formats:**
    - DICOM (.dcm)
    - PNG (.png)
    - JPEG (.jpg, .jpeg)
    - TIFF (.tif, .tiff)

    **Parameters:**
    - `file`: Image file to upload
    - `image_type`: Type of image (panoramic, periapical, bitewing, dicom)
    - `convert_dicom`: Whether to convert DICOM to PNG (default: True)
    """
    # Validate file extension
    allowed_extensions = {".dcm", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed: {allowed_extensions}"
        )

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        dicom_service = DICOMService(db)

        # Check if DICOM
        if dicom_service.is_dicom_file(temp_path):
            # Process DICOM
            image, converted_path = dicom_service.process_dicom_upload(
                dicom_file_path=temp_path,
                user_id=current_user.id,
                convert_to_png=convert_dicom,
            )
            message = "DICOM file uploaded and processed successfully"

        else:
            # Process standard image
            import cv2
            import os

            img = cv2.imread(temp_path)
            if img is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not read image file"
                )

            height, width = img.shape[:2]

            # Save to uploads directory
            upload_dir = Path("./uploads/images")
            upload_dir.mkdir(parents=True, exist_ok=True)
            permanent_path = upload_dir / file.filename
            shutil.move(temp_path, permanent_path)

            # Create image record
            image = Image(
                user_id=current_user.id,
                filename=file.filename,
                original_filename=file.filename,
                file_path=str(permanent_path),
                image_type=ImageType(image_type),
                status=ImageStatus.UPLOADED,
                width=width,
                height=height,
                file_size=os.path.getsize(permanent_path),
            )
            db.add(image)
            db.commit()
            db.refresh(image)

            converted_path = None
            message = "Image uploaded successfully"

        return {
            "image": image,
            "converted_path": converted_path,
            "message": message
        }

    except Exception as e:
        # Clean up temp file
        if Path(temp_path).exists():
            Path(temp_path).unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.get("/", response_model=List[ImageResponse])
async def list_images(
    skip: int = 0,
    limit: int = 100,
    image_type: Optional[str] = None,
    dataset_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List images (filtered by user unless admin)
    """
    query = db.query(Image)

    # Non-admin users can only see their own images or dataset images
    if not current_user.is_admin:
        query = query.filter(
            (Image.user_id == current_user.id) | (Image.dataset_id.isnot(None))
        )

    if image_type:
        query = query.filter(Image.image_type == image_type)

    if dataset_id:
        query = query.filter(Image.dataset_id == dataset_id)

    images = query.offset(skip).limit(limit).all()
    return images


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get image by ID
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

    return image


@router.get("/{image_id}/download")
async def download_image(
    image_id: int,
    dicom: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download image file

    **Parameters:**
    - `dicom`: If True and available, download original DICOM file
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

    # Determine file path
    if dicom and image.dicom_path:
        file_path = image.dicom_path
    else:
        file_path = image.file_path

    if not Path(file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on server"
        )

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=image.filename
    )


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an image (only owner or admin)
    """
    image = db.query(Image).filter(Image.id == image_id).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Check permissions
    if not current_user.is_admin and image.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this image"
        )

    # Delete file
    if Path(image.file_path).exists():
        Path(image.file_path).unlink()

    if image.dicom_path and Path(image.dicom_path).exists():
        Path(image.dicom_path).unlink()

    db.delete(image)
    db.commit()

    return {"message": "Image deleted successfully"}
