"""EfficientNet-B0 Setup"""
import torch.nn as nn
from torchvision import models

def get_model(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
    model = models.efficientnet_b0(weights=weights)
    model.classifier = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(model.classifier[1].in_features, num_classes),
    )
    return model
