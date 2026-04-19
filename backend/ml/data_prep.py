"""Downloads labeled images from S3 into ImageFolder structure for PyTorch training"""
import logging
import os
import random
import shutil
from pathlib import Path

from ml.config import MODEL_LABELS, TRAINING_DATA_DIR, TRAIN_SPLIT, VAL_SPLIT, TEST_SPLIT, RANDOM_SEED
from services.s3_service import s3_service

logger = logging.getLogger(__name__)

#helper func used by both "prepare" funcs to avoid repetition of mkdir + download loop
def _download_to(urls: list, dest_dir: Path) -> int:
    dest_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for url in urls:
        local_path = str(dest_dir / os.path.basename(url))
        if s3_service.download_file(url, local_path):
            count += 1
    return count

def prepare_training_data() -> tuple[Path, Path, Path]:
    cleanup_training_data()

    train_dir = TRAINING_DATA_DIR / "train"
    val_dir = TRAINING_DATA_DIR / "val"
    test_dir = TRAINING_DATA_DIR / "test"

    random.seed(RANDOM_SEED)

    downloaded_count = 0

    for label, prefix in MODEL_LABELS.items():
        print(f"Listing images for label '{label}' (prefix: {prefix})...")
        urls = s3_service.list_objects(prefix)

        if not urls:
            print(f"  WARNING: No images found under prefix '{prefix}'")
            continue

        #shuffle and split into train/val/test (80/10/10)
        random.shuffle(urls)
        train_end = int(len(urls) * TRAIN_SPLIT)
        val_end = train_end + int(len(urls) * VAL_SPLIT)
        test_end = val_end + int(len(urls) * TEST_SPLIT)
        train_urls = urls[:train_end]
        val_urls = urls[train_end:val_end]
        test_urls = urls[val_end:test_end]

        print(f"  Found {len(urls)} images — {len(train_urls)} train, {len(val_urls)} val, {len(test_urls)} test")
        
        downloaded_count += _download_to(train_urls, train_dir / label)
        downloaded_count += _download_to(val_urls, val_dir / label)
        downloaded_count += _download_to(test_urls, test_dir / label)


    print(f"Downloaded {downloaded_count} images total")

    if downloaded_count == 0:
        raise RuntimeError(
            "No images were downloaded from S3. "
            "Check that your S3 bucket has images under the prefixes: "
            f"{list(MODEL_LABELS.values())}"
        )

    return train_dir, val_dir, test_dir


#func skips train/val/test splitting — cross-validation in train.py handles the splits instead
def prepare_all_data() -> Path:
    cleanup_training_data()

    all_dir = TRAINING_DATA_DIR / "all"
    downloaded_count = 0

    for label, prefix in MODEL_LABELS.items():
        print(f"Listing images for label '{label}' (prefix: {prefix})...")
        urls = s3_service.list_objects(prefix)

        if not urls:
            print(f"  WARNING: No images found under prefix '{prefix}'")
            continue

        print(f"  Found {len(urls)} images")
        downloaded_count += _download_to(urls, all_dir / label)


    print(f"Downloaded {downloaded_count} images total")

    if downloaded_count == 0:
        raise RuntimeError(
            "No images were downloaded from S3. "
            "Check that your S3 bucket has images under the prefixes: "
            f"{list(MODEL_LABELS.values())}"
        )

    return all_dir


def cleanup_training_data():
    if TRAINING_DATA_DIR.exists():
        shutil.rmtree(TRAINING_DATA_DIR)
        logger.info(f"Cleaned up training data at {TRAINING_DATA_DIR}")
