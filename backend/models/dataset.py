from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from services.database import Base


class Dataset(Base):
    """
    Model for storing Kaggle dataset metadata and configuration
    """
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    kaggle_path = Column(String, nullable=False)  # e.g., "humansintheloop/teeth-segmentation-on-dental-x-ray-images"
    local_path = Column(String, nullable=True)  # Local storage path
    version = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    total_images = Column(Integer, default=0)
    total_annotations = Column(Integer, default=0)
    extra_metadata = Column(JSON, nullable=True)  # Store additional dataset info
    is_downloaded = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
