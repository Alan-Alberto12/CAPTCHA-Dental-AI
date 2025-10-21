"""
Teeth Segmentation Model Service

Handles ML model inference for teeth segmentation on dental X-ray images.
Supports multiple architectures: U-Net, Mask R-CNN, DeepLabV3, etc.
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
import cv2
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image as PILImage
from sqlalchemy.orm import Session
from models.image import Image
from models.prediction import Prediction, SegmentationModel


class UNet(nn.Module):
    """
    Simple U-Net architecture for teeth segmentation
    This is a placeholder - you'll want to use a pre-trained model or train your own
    """

    def __init__(self, in_channels=1, num_classes=32):
        super(UNet, self).__init__()

        # Encoder
        self.enc1 = self._conv_block(in_channels, 64)
        self.enc2 = self._conv_block(64, 128)
        self.enc3 = self._conv_block(128, 256)
        self.enc4 = self._conv_block(256, 512)

        # Bottleneck
        self.bottleneck = self._conv_block(512, 1024)

        # Decoder
        self.upconv4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec4 = self._conv_block(1024, 512)
        self.upconv3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = self._conv_block(512, 256)
        self.upconv2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = self._conv_block(256, 128)
        self.upconv1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = self._conv_block(128, 64)

        # Final layer
        self.out = nn.Conv2d(64, num_classes, kernel_size=1)

        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

    def _conv_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool(enc1))
        enc3 = self.enc3(self.pool(enc2))
        enc4 = self.enc4(self.pool(enc3))

        # Bottleneck
        bottleneck = self.bottleneck(self.pool(enc4))

        # Decoder
        dec4 = self.upconv4(bottleneck)
        dec4 = torch.cat([dec4, enc4], dim=1)
        dec4 = self.dec4(dec4)

        dec3 = self.upconv3(dec4)
        dec3 = torch.cat([dec3, enc3], dim=1)
        dec3 = self.dec3(dec3)

        dec2 = self.upconv2(dec3)
        dec2 = torch.cat([dec2, enc2], dim=1)
        dec2 = self.dec2(dec2)

        dec1 = self.upconv1(dec2)
        dec1 = torch.cat([dec1, enc1], dim=1)
        dec1 = self.dec1(dec1)

        return self.out(dec1)


class SegmentationService:
    """Service for teeth segmentation inference"""

    def __init__(
        self,
        db: Session,
        model_dir: str = "./models",
        device: str = "cpu"
    ):
        self.db = db
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.loaded_models = {}  # Cache for loaded models

    def get_or_create_default_model(self) -> SegmentationModel:
        """
        Get or create the default segmentation model

        Returns:
            SegmentationModel object
        """
        model = self.db.query(SegmentationModel).filter(
            SegmentationModel.is_default == True
        ).first()

        if not model:
            # Create a default model entry
            model = SegmentationModel(
                name="Default U-Net",
                version="1.0",
                architecture="U-Net",
                model_path=str(self.model_dir / "unet_default.pth"),
                num_classes=32,
                input_size=[512, 512],
                is_active=True,
                is_default=True,
            )
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)

        return model

    def load_model(self, model_id: int) -> Tuple[nn.Module, SegmentationModel]:
        """
        Load a segmentation model

        Args:
            model_id: Model ID

        Returns:
            Tuple of (PyTorch model, SegmentationModel object)
        """
        # Check cache
        if model_id in self.loaded_models:
            return self.loaded_models[model_id]

        # Get model from database
        model_record = self.db.query(SegmentationModel).filter(
            SegmentationModel.id == model_id
        ).first()

        if not model_record:
            raise ValueError(f"Model {model_id} not found")

        # Initialize model architecture
        if model_record.architecture.lower() == "u-net":
            model = UNet(in_channels=1, num_classes=model_record.num_classes)
        else:
            raise ValueError(f"Unsupported architecture: {model_record.architecture}")

        # Load weights if they exist
        if os.path.exists(model_record.model_path):
            try:
                state_dict = torch.load(
                    model_record.model_path,
                    map_location=self.device
                )
                model.load_state_dict(state_dict)
            except Exception as e:
                print(f"Warning: Could not load model weights: {e}")
                print("Using randomly initialized model")

        model = model.to(self.device)
        model.eval()

        # Cache the model
        self.loaded_models[model_id] = (model, model_record)

        return model, model_record

    def preprocess_image(
        self,
        image_path: str,
        target_size: Tuple[int, int] = (512, 512)
    ) -> Tuple[torch.Tensor, np.ndarray, Tuple[int, int]]:
        """
        Preprocess image for model inference

        Args:
            image_path: Path to image
            target_size: Target size for model input

        Returns:
            Tuple of (preprocessed tensor, original image, original size)
        """
        # Read image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        original_size = image.shape[:2]

        # Resize
        image_resized = cv2.resize(image, target_size)

        # Normalize to [0, 1]
        image_normalized = image_resized.astype(np.float32) / 255.0

        # Convert to tensor
        tensor = torch.from_numpy(image_normalized).unsqueeze(0).unsqueeze(0)
        tensor = tensor.to(self.device)

        return tensor, image, original_size

    def predict(
        self,
        image_id: int,
        model_id: Optional[int] = None,
        user_id: Optional[int] = None,
        confidence_threshold: float = 0.5,
    ) -> List[Prediction]:
        """
        Run segmentation prediction on an image

        Args:
            image_id: Image ID
            model_id: Model ID (uses default if None)
            user_id: User ID who requested prediction
            confidence_threshold: Minimum confidence for predictions

        Returns:
            List of Prediction objects
        """
        # Get image
        image = self.db.query(Image).filter(Image.id == image_id).first()
        if not image:
            raise ValueError(f"Image {image_id} not found")

        # Get model
        if model_id is None:
            model_record = self.get_or_create_default_model()
            model_id = model_record.id
        else:
            model_record = self.db.query(SegmentationModel).filter(
                SegmentationModel.id == model_id
            ).first()

        model, model_record = self.load_model(model_id)

        # Preprocess image
        input_tensor, original_image, original_size = self.preprocess_image(
            image.file_path,
            target_size=tuple(model_record.input_size) if model_record.input_size else (512, 512)
        )

        # Run inference
        start_time = time.time()
        with torch.no_grad():
            output = model(input_tensor)
            # Apply softmax to get probabilities
            probabilities = torch.softmax(output, dim=1)

        inference_time = time.time() - start_time

        # Post-process predictions
        predictions = self._postprocess_predictions(
            probabilities,
            original_size,
            image_id,
            model_id,
            user_id,
            confidence_threshold,
            inference_time
        )

        # Update image status
        image.is_predicted = True
        self.db.commit()

        return predictions

    def _postprocess_predictions(
        self,
        probabilities: torch.Tensor,
        original_size: Tuple[int, int],
        image_id: int,
        model_id: int,
        user_id: Optional[int],
        confidence_threshold: float,
        inference_time: float,
    ) -> List[Prediction]:
        """
        Post-process model predictions to extract tooth instances

        Args:
            probabilities: Model output probabilities [1, num_classes, H, W]
            original_size: Original image size
            image_id: Image ID
            model_id: Model ID
            user_id: User ID
            confidence_threshold: Confidence threshold
            inference_time: Time taken for inference

        Returns:
            List of Prediction objects
        """
        predictions = []

        # Get class predictions
        class_predictions = torch.argmax(probabilities, dim=1).squeeze().cpu().numpy()
        max_probs = torch.max(probabilities, dim=1)[0].squeeze().cpu().numpy()

        # Resize to original size
        class_predictions = cv2.resize(
            class_predictions.astype(np.uint8),
            (original_size[1], original_size[0]),
            interpolation=cv2.INTER_NEAREST
        )
        max_probs = cv2.resize(
            max_probs,
            (original_size[1], original_size[0]),
            interpolation=cv2.INTER_LINEAR
        )

        # Extract each tooth class (skip background class 0)
        unique_classes = np.unique(class_predictions)
        for tooth_class in unique_classes:
            if tooth_class == 0:  # Skip background
                continue

            # Create mask for this tooth
            mask = (class_predictions == tooth_class).astype(np.uint8)

            # Get confidence for this tooth
            tooth_confidence = max_probs[mask > 0].mean()

            if tooth_confidence < confidence_threshold:
                continue

            # Find contours
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if not contours:
                continue

            # Use largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            # Skip very small detections
            if area < 100:
                continue

            # Convert contour to polygon points
            polygon_points = largest_contour.squeeze().tolist()
            if len(polygon_points) < 3:
                continue

            # Get bounding box
            x, y, w, h = cv2.boundingRect(largest_contour)
            bbox = [int(x), int(y), int(x + w), int(y + h)]

            # Create prediction record
            prediction = Prediction(
                image_id=image_id,
                model_id=model_id,
                user_id=user_id,
                tooth_class=int(tooth_class),
                polygon_points=polygon_points,
                bbox=bbox,
                area=float(area),
                confidence_score=float(tooth_confidence),
                inference_time=inference_time,
            )

            self.db.add(prediction)
            predictions.append(prediction)

        self.db.commit()
        return predictions

    def visualize_predictions(
        self,
        image_path: str,
        predictions: List[Prediction],
        output_path: Optional[str] = None,
    ) -> np.ndarray:
        """
        Visualize predictions on the image

        Args:
            image_path: Path to original image
            predictions: List of predictions
            output_path: Optional path to save visualization

        Returns:
            Visualization image array
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        # Convert to BGR for color visualization
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Draw predictions
        for pred in predictions:
            # Generate color based on tooth class
            color = self._get_color_for_class(pred.tooth_class)

            # Draw polygon
            points = np.array(pred.polygon_points, dtype=np.int32)
            cv2.polylines(image, [points], True, color, 2)

            # Draw bounding box
            if pred.bbox:
                x1, y1, x2, y2 = pred.bbox
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 1)

            # Add label
            if pred.bbox:
                label = f"Tooth {pred.tooth_class}: {pred.confidence_score:.2f}"
                cv2.putText(
                    image, label, (pred.bbox[0], pred.bbox[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1
                )

        # Save if output path provided
        if output_path:
            cv2.imwrite(output_path, image)

        return image

    def _get_color_for_class(self, class_id: int) -> Tuple[int, int, int]:
        """Get a unique color for a class ID"""
        np.random.seed(class_id)
        return tuple(np.random.randint(0, 255, 3).tolist())

    def calculate_metrics(
        self,
        predictions: List[Prediction],
        annotations: List
    ) -> Dict:
        """
        Calculate evaluation metrics (IoU, Dice, etc.)

        Args:
            predictions: List of predictions
            annotations: List of ground truth annotations

        Returns:
            Dictionary of metrics
        """
        # This is a placeholder - implement based on your needs
        return {
            "num_predictions": len(predictions),
            "num_annotations": len(annotations),
            "mean_confidence": np.mean([p.confidence_score for p in predictions]) if predictions else 0,
        }
