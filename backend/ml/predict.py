"""EfficientNet-B0 Prediction Service"""
import logging
from io import BytesIO
from pathlib import Path
from typing import Optional

import torch
import torch.nn.functional as F
from PIL import Image as PILImage
from torchvision import transforms

from ml.config import IMAGE_SIZE, ML_MODELS_DIR
from ml.models.classifier import get_model

logger = logging.getLogger(__name__)


class PredictionService:
    _instance = None

    def __init__(self):
        self.model = None
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        self.class_to_idx = None
        self.idx_to_class = None
        self.arch = None

    @classmethod
    def get_instance(cls) -> "PredictionService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self, model_path: Optional[str] = None) -> bool:
        #load checkpoint from path (or latest.pth if no path given). Returns True on success
        if model_path is None:
            path = ML_MODELS_DIR / "latest.pth"
        else:
            path = Path(model_path)

        if not path.exists():
            logger.warning(f"Model file not found: {path}")
            return False

        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        self.arch = checkpoint["arch"]
        self.class_to_idx = checkpoint["class_to_idx"]
        self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}

        self.model = get_model(
            num_classes=checkpoint["num_classes"],
            pretrained=False,
        )
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()

        logger.info(f"Loaded model: {self.arch} from {path}")
        return True

    def predict(self, image_bytes: bytes) -> dict:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        image = PILImage.open(BytesIO(image_bytes)).convert("RGB")
        img_tensor = self.transform(image).unsqueeze(0).to(self.device) # add batch dimension

        with torch.no_grad():
            outputs = self.model(img_tensor)
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)

        predicted_label = self.idx_to_class[predicted_idx.item()]

        return {
            "label": predicted_label,
            "confidence": round(confidence.item(), 4),
        }
