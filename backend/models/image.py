from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from services.database import Base


class ImageType(str, enum.Enum):
    """Enum for image types"""
    PANORAMIC = "panoramic"
    PERIAPICAL = "periapical"
    BITEWING = "bitewing"
    DICOM = "dicom"
    OTHER = "other"


class ImageStatus(str, enum.Enum):
    """Enum for image processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Image(Base):
    """
    Model for storing dental X-ray images from Kaggle dataset and user uploads
    """
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=True)  # Null for user uploads
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # User who uploaded

    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    file_path = Column(String, nullable=False)  # Path to stored image
    dicom_path = Column(String, nullable=True)  # Path to DICOM file if applicable

    image_type = Column(Enum(ImageType), default=ImageType.PANORAMIC)
    status = Column(Enum(ImageStatus), default=ImageStatus.UPLOADED)

    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)  # In bytes

    # DICOM metadata
    dicom_metadata = Column(JSON, nullable=True)
    patient_id = Column(String, nullable=True)
    study_date = Column(DateTime(timezone=True), nullable=True)

    # Processing info
    is_annotated = Column(Boolean, default=False)
    is_predicted = Column(Boolean, default=False)
    annotation_count = Column(Integer, default=0)

    extra_metadata = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    dataset = relationship("Dataset", backref="images")
    user = relationship("User", backref="images")
