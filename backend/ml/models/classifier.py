"""
CNN architecture wrapper — supports ResNet50, EfficientNet-B0, DenseNet121.
Uses modern torchvision weights API.
"""

import torch.nn as nn
from torchvision import models


def get_model(arch: str = "resnet50", num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """
    Returns a CNN with the final layer replaced for binary classification.

    Args:
        arch: Model architecture ("resnet50", "efficientnet_b0", "densenet121")
        num_classes: Number of output classes
        pretrained: Whether to use ImageNet pretrained weights

    Returns:
        PyTorch model ready for training or inference
    """
    if arch == "resnet50":
        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        model = models.resnet50(weights=weights)
        model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(model.fc.in_features, num_classes),
        )

    elif arch == "efficientnet_b0":
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        model = models.efficientnet_b0(weights=weights)
        model.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(model.classifier[1].in_features, num_classes),
        )

    elif arch == "densenet121":
        weights = models.DenseNet121_Weights.DEFAULT if pretrained else None
        model = models.densenet121(weights=weights)
        model.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(model.classifier.in_features, num_classes),
        )

    else:
        raise ValueError(f"Unsupported architecture: {arch}. Use resnet50, efficientnet_b0, or densenet121.")

    return model
