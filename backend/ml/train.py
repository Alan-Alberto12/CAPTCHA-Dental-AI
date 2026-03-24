#!/usr/bin/env python
"""
Standalone CNN training script for dental image binary classification.

Usage (from backend/ directory):
    python -m ml.train
    python -m ml.train --arch efficientnet_b0 --epochs 10 --batch-size 16
"""

import argparse
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from ml.config import (
    BATCH_SIZE,
    DEFAULT_MODEL_ARCH,
    EARLY_STOP_PATIENCE,
    IMAGE_SIZE,
    LEARNING_RATE,
    ML_MODELS_DIR,
    NUM_CLASSES,
    NUM_EPOCHS,
    SCHEDULER_PATIENCE,
)
from ml.data_prep import cleanup_training_data, prepare_training_data
from ml.models.classifier import get_model

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_transforms():
    """Training transforms with augmentation, validation without."""
    train_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    return train_transform, val_transform


def train_epoch(model, loader, criterion, optimizer):
    """Run one training epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    return running_loss / len(loader), 100 * correct / total


def validate(model, loader, criterion):
    """Run validation and return loss, accuracy, predictions, and labels."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    return running_loss / len(loader), 100 * correct / total, all_preds, all_labels


def train_model(
    arch: str = DEFAULT_MODEL_ARCH,
    epochs: int = NUM_EPOCHS,
    batch_size: int = BATCH_SIZE,
    lr: float = LEARNING_RATE,
) -> dict:
    """
    Full training pipeline:
    1. Download labeled images from S3
    2. Train the CNN
    3. Evaluate on validation set
    4. Save .pth checkpoint
    5. Clean up temporary data

    Returns:
        Dict with model path, architecture, and metrics
    """
    print(f"\nUsing device: {DEVICE}")
    print(f"Architecture: {arch}, Epochs: {epochs}, Batch size: {batch_size}, LR: {lr}")

    # --- Step 1: Prepare data from S3 ---
    print("\n" + "=" * 60)
    print("DOWNLOADING TRAINING DATA FROM S3")
    print("=" * 60)

    train_dir, val_dir = prepare_training_data()

    train_transform, val_transform = get_transforms()
    train_dataset = datasets.ImageFolder(str(train_dir), transform=train_transform)
    val_dataset = datasets.ImageFolder(str(val_dir), transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    print(f"\nClasses: {train_dataset.classes}")
    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")

    if len(train_dataset) < 10:
        print("WARNING: Very few training samples. Results may be unreliable.")

    # --- Step 2: Build model ---
    model = get_model(arch=arch, num_classes=NUM_CLASSES).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", patience=SCHEDULER_PATIENCE, factor=0.5
    )

    # --- Step 3: Training loop ---
    print("\n" + "=" * 60)
    print("TRAINING")
    print("=" * 60)

    best_val_acc = 0.0
    patience_counter = 0

    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_acc, _, _ = validate(model, val_loader, criterion)

        scheduler.step(val_loss)

        print(
            f"Epoch {epoch + 1:02d}/{epochs} | "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            # Save best model to a temp location (will be copied later)
            ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), ML_MODELS_DIR / "_best_temp.pth")
            print(f"  -> New best model (Val Acc: {val_acc:.2f}%)")
        else:
            patience_counter += 1

        if patience_counter >= EARLY_STOP_PATIENCE:
            print(f"\nEarly stopping after {epoch + 1} epochs")
            break

    # --- Step 4: Final evaluation with best model ---
    print("\n" + "=" * 60)
    print("FINAL EVALUATION")
    print("=" * 60)

    best_temp_path = ML_MODELS_DIR / "_best_temp.pth"
    if best_temp_path.exists():
        model.load_state_dict(torch.load(best_temp_path, map_location=DEVICE, weights_only=True))
        best_temp_path.unlink()

    _, final_acc, final_preds, final_labels = validate(model, val_loader, criterion)

    report = classification_report(
        final_labels, final_preds,
        target_names=train_dataset.classes,
        output_dict=True,
    )
    report_str = classification_report(
        final_labels, final_preds,
        target_names=train_dataset.classes,
    )
    cm = confusion_matrix(final_labels, final_preds)

    print(f"\nBest Validation Accuracy: {final_acc:.2f}%")
    print(f"\nClassification Report:\n{report_str}")
    print(f"Confusion Matrix:\n{cm}")

    # --- Step 5: Save final checkpoint ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_filename = f"{arch}_{timestamp}.pth"

    checkpoint = {
        "model_state_dict": model.state_dict(),
        "arch": arch,
        "num_classes": NUM_CLASSES,
        "class_to_idx": train_dataset.class_to_idx,
        "metrics": report,
        "best_val_acc": best_val_acc,
        "trained_at": timestamp,
    }

    model_path = ML_MODELS_DIR / model_filename
    torch.save(checkpoint, model_path)

    latest_path = ML_MODELS_DIR / "latest.pth"
    torch.save(checkpoint, latest_path)

    # Verify the files were actually saved
    if model_path.exists() and latest_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"\n{'=' * 60}")
        print(f"MODEL SAVED SUCCESSFULLY")
        print(f"{'=' * 60}")
        print(f"  File: {model_path}")
        print(f"  Latest: {latest_path}")
        print(f"  Size: {size_mb:.1f} MB")
        print(f"  Architecture: {arch}")
        print(f"  Best Val Acc: {best_val_acc:.2f}%")
        print(f"{'=' * 60}")
    else:
        print(f"\nWARNING: Model save FAILED!")
        print(f"  Expected path: {model_path}")
        print(f"  Exists: {model_path.exists()}")
        print(f"  Latest exists: {latest_path.exists()}")

    # --- Step 6: Clean up ---
    cleanup_training_data()

    return {
        "model_path": str(model_path),
        "architecture": arch,
        "epochs": epochs,
        "best_val_acc": best_val_acc,
        "metrics": report,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train dental image CNN classifier")
    parser.add_argument(
        "--arch", default=DEFAULT_MODEL_ARCH,
        choices=["resnet50", "efficientnet_b0", "densenet121"],
        help="Model architecture",
    )
    parser.add_argument("--epochs", type=int, default=NUM_EPOCHS, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Batch size")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Learning rate")
    args = parser.parse_args()

    results = train_model(
        arch=args.arch,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
    )

    print(f"\nTraining complete. Best Val Acc: {results['best_val_acc']:.2f}%")
