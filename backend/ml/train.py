#!/usr/bin/env python
"""
Standalone CNN training script for dental image binary classification.

Usage (from backend/ directory):
    python -m ml.train
    python -m ml.train --arch efficientnet_b0 --epochs 10 --batch-size 16
"""

import argparse
from datetime import datetime

# matplotlib: used to save ROC curve plot after cross-validation
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for saving files
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms

from ml.config import (
    BATCH_SIZE,
    DEFAULT_MODEL_ARCH,
    EARLY_STOP_PATIENCE,
    IMAGE_SIZE,
    LEARNING_RATE,
    ML_MODELS_DIR,
    N_FOLDS,
    NUM_CLASSES,
    NUM_EPOCHS,
    RANDOM_SEED,
    SCHEDULER_PATIENCE,
)
from ml.data_prep import cleanup_training_data, prepare_all_data
from ml.models.classifier import get_model

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
elif torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")


def save_roc_curve(fpr, tpr, auc_score, fold_results, output_path):
    """
    Save ROC curve plot to a PNG file.
    Called after cross-validation using the aggregated held-out predictions.
    Plots each fold's curve (for variance context) plus the aggregated curve.
    """
    fig, ax = plt.subplots(figsize=(7, 6))

    # Per-fold curves (light, for context)
    for r in fold_results:
        fold_probs = [p[1] for p in r["probs"]]
        f_fpr, f_tpr, _ = roc_curve(r["labels"], fold_probs)
        ax.plot(f_fpr, f_tpr, color="steelblue", alpha=0.3, linewidth=1,
                label=f"Fold {r['fold']} (AUC={r['auc']:.3f})")

    # Aggregated curve across all folds (bold)
    ax.plot(fpr, tpr, color="crimson", linewidth=2.5,
            label=f"Aggregated CV (AUC={auc_score:.3f})")

    # Diagonal reference line (random classifier baseline)
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random classifier")

    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curve — EfficientNet-B0 (Cross-Validation)", fontsize=13)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.02])

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


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
    """Run validation and return loss, accuracy, predictions, labels, and probabilities."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    all_probs = []

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            probs = torch.softmax(outputs, dim=1)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    return running_loss / len(loader), 100 * correct / total, all_preds, all_labels, all_probs


def train_model(
    arch: str = DEFAULT_MODEL_ARCH,
    epochs: int = NUM_EPOCHS,
    batch_size: int = BATCH_SIZE,
    lr: float = LEARNING_RATE,
) -> dict:
    """
    Full training pipeline with 3-fold cross-validation:
    1. Download all labeled images from S3
    2. Run N_FOLDS CV folds — train, evaluate, collect metrics per fold
    3. Print averaged CV metrics and aggregated ROC curve
    4. Retrain final model on full dataset using avg epochs from CV
    5. Save .pth checkpoint and clean up

    Returns:
        Dict with model path, architecture, and CV metrics
    """
    print(f"\nUsing device: {DEVICE}")
    print(f"Architecture: {arch}, Epochs: {epochs}, Batch size: {batch_size}, LR: {lr}")

    # --- Step 1: Download all data from S3 ---
    print("\n" + "=" * 60)
    print("DOWNLOADING TRAINING DATA FROM S3")
    print("=" * 60)

    all_dir = prepare_all_data()

    train_transform, val_transform = get_transforms()

    # Two dataset instances of the same directory — one per transform
    # Subsets index into these, so train indices get augmentation, val indices don't
    full_train_ds = datasets.ImageFolder(str(all_dir), transform=train_transform)
    full_val_ds = datasets.ImageFolder(str(all_dir), transform=val_transform)

    class_names = full_train_ds.classes
    targets = np.array(full_train_ds.targets)

    print(f"\nClasses: {class_names}")
    print(f"Total samples: {len(full_train_ds)}")

    # --- Step 2: 3-Fold Cross-Validation ---
    print("\n" + "=" * 60)
    print(f"{N_FOLDS}-FOLD CROSS-VALIDATION")
    print("=" * 60)

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    fold_results = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(np.zeros(len(targets)), targets)):
        print(f"\n--- Fold {fold + 1}/{N_FOLDS} ---")
        print(f"  Train: {len(train_idx)} samples | Val: {len(val_idx)} samples")

        train_loader = DataLoader(
            Subset(full_train_ds, train_idx), batch_size=batch_size, shuffle=True, num_workers=0
        )
        val_loader = DataLoader(
            Subset(full_val_ds, val_idx), batch_size=batch_size, shuffle=False, num_workers=0
        )

        # Class weights from this fold's training split
        fold_targets = targets[train_idx]
        class_counts = torch.tensor(
            [np.sum(fold_targets == i) for i in range(len(class_names))],
            dtype=torch.float,
        )
        class_weights = class_counts.sum() / (len(class_counts) * class_counts)

        model = get_model(arch=arch, num_classes=NUM_CLASSES).to(DEVICE)
        criterion = nn.CrossEntropyLoss(weight=class_weights.to(DEVICE))
        optimizer = optim.Adam(model.parameters(), lr=lr)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="min", patience=SCHEDULER_PATIENCE, factor=0.5
        )

        best_val_acc = 0.0
        patience_counter = 0
        best_epoch = 0
        temp_path = ML_MODELS_DIR / f"_fold{fold + 1}_best.pth"

        for epoch in range(epochs):
            train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer)
            val_loss, val_acc, _, _, _ = validate(model, val_loader, criterion)
            scheduler.step(val_loss)

            print(
                f"  Epoch {epoch + 1:02d}/{epochs} | "
                f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
                f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%"
            )

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                patience_counter = 0
                best_epoch = epoch + 1
                torch.save(model.state_dict(), temp_path)
                print(f"    -> New best (Val Acc: {val_acc:.2f}%)")
            else:
                patience_counter += 1

            if patience_counter >= EARLY_STOP_PATIENCE:
                print(f"  Early stopping at epoch {epoch + 1}")
                break

        # Evaluate best model for this fold
        if temp_path.exists():
            model.load_state_dict(torch.load(temp_path, map_location=DEVICE, weights_only=True))
            temp_path.unlink()

        _, fold_acc, fold_preds, fold_labels, fold_probs = validate(model, val_loader, criterion)

        cm = confusion_matrix(fold_labels, fold_preds)
        tn, fp, fn, tp = cm.ravel()
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        pos_probs = [p[1] for p in fold_probs]
        auc = roc_auc_score(fold_labels, pos_probs)

        print(
            f"\n  Fold {fold + 1} Results — "
            f"Acc: {fold_acc:.2f}% | Sensitivity: {sensitivity:.4f} | "
            f"Specificity: {specificity:.4f} | AUC: {auc:.4f}"
        )

        fold_results.append({
            "fold": fold + 1,
            "acc": fold_acc,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "auc": auc,
            "best_epoch": best_epoch,
            "preds": fold_preds,
            "labels": fold_labels,
            "probs": fold_probs,
        })

    # --- Step 3: Print CV summary ---
    print("\n" + "=" * 60)
    print(f"{N_FOLDS}-FOLD CROSS-VALIDATION SUMMARY")
    print("=" * 60)

    for r in fold_results:
        print(
            f"  Fold {r['fold']} — Acc: {r['acc']:.2f}% | "
            f"Sensitivity: {r['sensitivity']:.4f} | Specificity: {r['specificity']:.4f} | "
            f"AUC: {r['auc']:.4f}"
        )

    mean_acc = np.mean([r["acc"] for r in fold_results])
    mean_sensitivity = np.mean([r["sensitivity"] for r in fold_results])
    mean_specificity = np.mean([r["specificity"] for r in fold_results])
    mean_auc = np.mean([r["auc"] for r in fold_results])
    avg_best_epoch = int(round(np.mean([r["best_epoch"] for r in fold_results])))

    print(f"\n  Mean Accuracy:    {mean_acc:.2f}%")
    print(f"  Mean Sensitivity: {mean_sensitivity:.4f}")
    print(f"  Mean Specificity: {mean_specificity:.4f}")
    print(f"  Mean AUC-ROC:     {mean_auc:.4f}")
    print(f"  Avg Best Epoch:   {avg_best_epoch}")

    # Aggregate all fold predictions for overall report and ROC curve
    all_preds = [p for r in fold_results for p in r["preds"]]
    all_labels = [l for r in fold_results for l in r["labels"]]
    all_probs = [p for r in fold_results for p in r["probs"]]

    report = classification_report(all_labels, all_preds, target_names=class_names, output_dict=True)
    report_str = classification_report(all_labels, all_preds, target_names=class_names)
    cm_all = confusion_matrix(all_labels, all_preds)
    pos_probs_all = [p[1] for p in all_probs]
    fpr, tpr, thresholds = roc_curve(all_labels, pos_probs_all)

    print(f"\nAggregated Classification Report:\n{report_str}")
    print(f"Aggregated Confusion Matrix:\n{cm_all}")
    print(f"\nROC Curve (aggregated, FPR -> TPR @ threshold):")
    step = max(1, len(fpr) // 10)
    for i in range(0, len(fpr), step):
        print(f"  FPR: {fpr[i]:.3f}  TPR: {tpr[i]:.3f}  Threshold: {thresholds[i]:.3f}")

    # Save ROC curve plot — uses aggregated CV predictions (validation set, not training data)
    roc_plot_path = ML_MODELS_DIR / "roc_curve.png"
    save_roc_curve(fpr, tpr, mean_auc, fold_results, roc_plot_path)
    print(f"\n  ROC curve saved to: {roc_plot_path}")

    # --- Step 4: Retrain final model on full dataset ---
    print("\n" + "=" * 60)
    print("FINAL MODEL TRAINING (full dataset)")
    print("=" * 60)
    print(f"Training for {avg_best_epoch} epochs (avg best epoch across folds)")

    full_loader = DataLoader(full_train_ds, batch_size=batch_size, shuffle=True, num_workers=0)

    class_counts_full = torch.tensor(
        [full_train_ds.targets.count(i) for i in range(len(class_names))],
        dtype=torch.float,
    )
    class_weights_full = class_counts_full.sum() / (len(class_counts_full) * class_counts_full)

    final_model = get_model(arch=arch, num_classes=NUM_CLASSES).to(DEVICE)
    final_criterion = nn.CrossEntropyLoss(weight=class_weights_full.to(DEVICE))
    final_optimizer = optim.Adam(final_model.parameters(), lr=lr)

    for epoch in range(avg_best_epoch):
        train_loss, train_acc = train_epoch(final_model, full_loader, final_criterion, final_optimizer)
        print(f"  Epoch {epoch + 1:02d}/{avg_best_epoch} | Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")

    # --- Step 5: Save checkpoint ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_filename = f"{arch}_{timestamp}.pth"

    checkpoint = {
        "model_state_dict": final_model.state_dict(),
        "arch": arch,
        "num_classes": NUM_CLASSES,
        "class_to_idx": full_train_ds.class_to_idx,
        "metrics": report,
        "cv_mean_acc": mean_acc,
        "cv_mean_auc": mean_auc,
        "cv_mean_sensitivity": mean_sensitivity,
        "cv_mean_specificity": mean_specificity,
        "trained_at": timestamp,
    }

    model_path = ML_MODELS_DIR / model_filename
    torch.save(checkpoint, model_path)
    latest_path = ML_MODELS_DIR / "latest.pth"
    torch.save(checkpoint, latest_path)

    if model_path.exists() and latest_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"\n{'=' * 60}")
        print(f"MODEL SAVED SUCCESSFULLY")
        print(f"{'=' * 60}")
        print(f"  File: {model_path}")
        print(f"  Latest: {latest_path}")
        print(f"  Size: {size_mb:.1f} MB")
        print(f"  Architecture: {arch}")
        print(f"  CV Mean Acc: {mean_acc:.2f}% | CV Mean AUC: {mean_auc:.4f}")
        print(f"{'=' * 60}")
    else:
        print(f"\nWARNING: Model save FAILED!")

    # --- Step 6: Clean up ---
    cleanup_training_data()

    return {
        "model_path": str(model_path),
        "architecture": arch,
        "cv_mean_acc": mean_acc,
        "cv_mean_auc": mean_auc,
        "cv_mean_sensitivity": mean_sensitivity,
        "cv_mean_specificity": mean_specificity,
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

    print(f"\nTraining complete. CV Mean Acc: {results['cv_mean_acc']:.2f}% | CV Mean AUC: {results['cv_mean_auc']:.4f}")
