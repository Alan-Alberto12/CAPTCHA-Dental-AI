from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from services.database import Base


class SegmentationModel(Base):
    """
    Model for storing trained segmentation models
    """
    __tablename__ = "segmentation_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    version = Column(String, nullable=False)
    architecture = Column(String, nullable=False)  # e.g., "U-Net", "Mask R-CNN", "DeepLabV3"

    model_path = Column(String, nullable=False)  # Path to saved model weights
    config_path = Column(String, nullable=True)  # Path to model configuration

    # Training info
    trained_on_dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=True)
    num_classes = Column(Integer, default=32)  # Number of tooth classes
    input_size = Column(JSON, nullable=True)  # [height, width]

    # Performance metrics
    accuracy = Column(Float, nullable=True)
    mean_iou = Column(Float, nullable=True)
    dice_coefficient = Column(Float, nullable=True)

    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    extra_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    dataset = relationship("Dataset", backref="models")


class Prediction(Base):
    """
    Model for storing AI predictions for teeth segmentation
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("segmentation_models.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Tooth information
    tooth_class = Column(Integer, nullable=False)
    tooth_notation = Column(String, nullable=True)

    # Segmentation data
    polygon_points = Column(JSON, nullable=False)  # Predicted polygon
    mask_path = Column(String, nullable=True)  # Path to segmentation mask
    bbox = Column(JSON, nullable=True)  # Bounding box
    area = Column(Float, nullable=True)

    # Prediction confidence
    confidence_score = Column(Float, nullable=False)
    is_verified = Column(Boolean, default=False)  # Human verified
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Processing info
    inference_time = Column(Float, nullable=True)  # Time taken in seconds

    extra_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    image = relationship("Image", foreign_keys=[image_id], backref="predictions")
    model = relationship("SegmentationModel", backref="predictions")
    user = relationship("User", foreign_keys=[user_id], backref="predictions")
    verifier = relationship("User", foreign_keys=[verified_by], backref="verified_predictions")
