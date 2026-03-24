"""
Script to download and process the Kaggle teeth segmentation dataset

Usage:
    python scripts/download_kaggle_dataset.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database import SessionLocal
from services.kaggle_service import KaggleDatasetService


def main():
    """Download and process the Kaggle teeth segmentation dataset"""

    # Create database session
    db = SessionLocal()

    try:
        print("=" * 60)
        print("Kaggle Teeth Segmentation Dataset Download")
        print("=" * 60)

        # Initialize Kaggle service
        kaggle_service = KaggleDatasetService(db)

        # Download dataset
        print("\n1. Downloading dataset from Kaggle...")
        print("   This may take several minutes depending on your internet speed.")

        kaggle_path = "humansintheloop/teeth-segmentation-on-dental-x-ray-images"
        local_path, dataset = kaggle_service.download_teeth_segmentation_dataset(
            kaggle_path=kaggle_path
        )

        print(f"\n   ✓ Dataset downloaded successfully!")
        print(f"   Local path: {local_path}")
        print(f"   Dataset ID: {dataset.id}")

        # Process annotations
        print("\n2. Processing annotations...")
        print("   Scanning for images and annotation files...")

        try:
            processed_count = kaggle_service.process_dataset_annotations(dataset)
            print(f"\n   ✓ Processed {processed_count} images successfully!")
        except Exception as e:
            print(f"\n   ⚠ Warning: Could not process annotations: {e}")
            print("   You may need to manually process the annotations later.")

        # Get statistics
        print("\n3. Dataset Statistics:")
        print("-" * 60)
        stats = kaggle_service.get_dataset_stats(dataset)

        print(f"   Name:              {stats['name']}")
        print(f"   Kaggle Path:       {stats['kaggle_path']}")
        print(f"   Total Images:      {stats['total_images']}")
        print(f"   Total Annotations: {stats['total_annotations']}")
        print(f"   Downloaded:        {stats['is_downloaded']}")
        print(f"   Processed:         {stats['is_processed']}")
        print(f"   Local Path:        {stats['local_path']}")

        print("\n" + "=" * 60)
        print("✓ Dataset setup complete!")
        print("=" * 60)

        print("\nNext steps:")
        print("1. Train a segmentation model on this dataset")
        print("2. Use the API to upload images and run predictions")
        print("3. Visualize results in the frontend")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    main()
