"""
Data preparation — downloads labeled images from S3 into ImageFolder structure
for PyTorch training.

Expects S3 bucket to have images organized under label prefixes:
  needs_review/image1.jpg
  needs_review/image2.jpg
  no_review/image3.jpg
  no_review/image4.jpg
"""

import logging
import os
import random
import shutil
from pathlib import Path
from typing import Tuple

from ml.config import S3_LABEL_PREFIXES, TRAINING_DATA_DIR, TRAIN_SPLIT, VAL_SPLIT, TEST_SPLIT, RANDOM_SEED
from services.s3_service import s3_service

logger = logging.getLogger(__name__)


def prepare_training_data() -> Tuple[Path, Path, Path]:
    """
    Download labeled images from S3 and organize into ImageFolder structure.

    Returns:
        (train_dir, val_dir, test_dir) paths ready for torchvision.datasets.ImageFolder
    """
    # Clean up any previous training data
    cleanup_training_data()

    train_dir = TRAINING_DATA_DIR / "train"
    val_dir = TRAINING_DATA_DIR / "val"
    test_dir = TRAINING_DATA_DIR / "test"

    random.seed(RANDOM_SEED)

    total_downloaded = 0

    for label, prefix in S3_LABEL_PREFIXES.items():
        print(f"Listing images for label '{label}' (prefix: {prefix})...")
        urls = s3_service.list_objects(prefix)

        if not urls:
            print(f"  WARNING: No images found under prefix '{prefix}'")
            continue

        # Shuffle and split into train/val/test (80/10/10)
        random.shuffle(urls)
        train_end = int(len(urls) * TRAIN_SPLIT)
        val_end = train_end + int(len(urls) * VAL_SPLIT)
        test_end = val_end + int(len(urls) * TEST_SPLIT)
        train_urls = urls[:train_end]
        val_urls = urls[train_end:val_end]
        test_urls = urls[val_end:test_end]

        print(f"  Found {len(urls)} images — {len(train_urls)} train, {len(val_urls)} val, {len(test_urls)} test")

        # Download train images
        train_label_dir = train_dir / label
        train_label_dir.mkdir(parents=True, exist_ok=True)
        for url in train_urls:
            filename = os.path.basename(url)
            local_path = str(train_label_dir / filename)
            if s3_service.download_file(url, local_path):
                total_downloaded += 1

        # Download val images
        val_label_dir = val_dir / label
        val_label_dir.mkdir(parents=True, exist_ok=True)
        for url in val_urls:
            filename = os.path.basename(url)
            local_path = str(val_label_dir / filename)
            if s3_service.download_file(url, local_path):
                total_downloaded += 1

        # Download test images
        test_label_dir = test_dir / label
        test_label_dir.mkdir(parents=True, exist_ok=True)
        for url in test_urls:
            filename = os.path.basename(url)
            local_path = str(test_label_dir / filename)
            if s3_service.download_file(url, local_path):
                total_downloaded += 1

    print(f"Downloaded {total_downloaded} images total")

    if total_downloaded == 0:
        raise RuntimeError(
            "No images were downloaded from S3. "
            "Check that your S3 bucket has images under the prefixes: "
            f"{list(S3_LABEL_PREFIXES.values())}"
        )

    return train_dir, val_dir, test_dir


def cleanup_training_data():
    """Remove temporary training data directory."""
    if TRAINING_DATA_DIR.exists():
        shutil.rmtree(TRAINING_DATA_DIR)
        logger.info(f"Cleaned up training data at {TRAINING_DATA_DIR}")
