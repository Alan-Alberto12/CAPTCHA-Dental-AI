from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from services.database import Base


class Annotation(Base):
    """
    Model for storing manual annotations from the Kaggle dataset
    Each tooth is segmented with a polygon
    """
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)

    # Tooth information
    tooth_class = Column(Integer, nullable=False)  # Class ID for the tooth (1-32 for adult teeth)
    tooth_notation = Column(String, nullable=True)  # e.g., "11", "21", "31", "41" (FDI notation)

    # Polygon segmentation data
    polygon_points = Column(JSON, nullable=False)  # List of [x, y] coordinates
    bbox = Column(JSON, nullable=True)  # Bounding box [x_min, y_min, x_max, y_max]
    area = Column(Float, nullable=True)  # Polygon area in pixels

    # Annotation metadata
    annotator_id = Column(String, nullable=True)  # ID of person who annotated
    confidence = Column(Float, nullable=True)  # Confidence score if available

    extra_metadata = Column(JSON, nullable=True)  # Additional annotation info
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    image = relationship("Image", backref="annotations")
