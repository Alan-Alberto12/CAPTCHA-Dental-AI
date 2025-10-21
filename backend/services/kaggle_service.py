"""
Kaggle Dataset Download and Management Service

This service handles downloading and processing the Kaggle teeth segmentation dataset:
https://www.kaggle.com/datasets/humansintheloop/teeth-segmentation-on-dental-x-ray-images
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import kagglehub
from sqlalchemy.orm import Session
from models.dataset import Dataset
from models.image import Image, ImageType, ImageStatus
from models.annotation import Annotation
import cv2
import numpy as np


class KaggleDatasetService:
    """Service for managing Kaggle dataset downloads and processing"""

    def __init__(self, db: Session, data_dir: str = "./data"):
        self.db = db
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def download_teeth_segmentation_dataset(
        self,
        kaggle_path: str = "humansintheloop/teeth-segmentation-on-dental-x-ray-images"
    ) -> Tuple[str, Dataset]:
        """
        Download the teeth segmentation dataset from Kaggle

        Args:
            kaggle_path: Kaggle dataset path

        Returns:
            Tuple of (local_path, Dataset object)
        """
        # Check if dataset already exists in DB
        dataset = self.db.query(Dataset).filter(
            Dataset.kaggle_path == kaggle_path
        ).first()

        if dataset and dataset.is_downloaded:
            print(f"Dataset already downloaded at: {dataset.local_path}")
            return dataset.local_path, dataset

        # Download dataset using kagglehub
        print(f"Downloading dataset: {kaggle_path}")
        download_path = kagglehub.dataset_download(kaggle_path)
        print(f"Dataset downloaded to: {download_path}")

        # Create or update dataset record
        if not dataset:
            dataset = Dataset(
                name="Teeth Segmentation on Dental X-ray Images",
                kaggle_path=kaggle_path,
                description="Manual teeth segmentation on panoramic dental radiography",
            )
            self.db.add(dataset)

        dataset.local_path = download_path
        dataset.is_downloaded = True
        self.db.commit()
        self.db.refresh(dataset)

        return download_path, dataset

    def process_dataset_annotations(
        self,
        dataset: Dataset,
        annotations_file: str = "annotations.json"
    ) -> int:
        """
        Process annotations from the Kaggle dataset

        The dataset typically contains:
        - Images in PNG/JPG format
        - Annotations in JSON format with polygon coordinates

        Args:
            dataset: Dataset object
            annotations_file: Name of annotations file

        Returns:
            Number of images processed
        """
        if not dataset.local_path or not os.path.exists(dataset.local_path):
            raise ValueError("Dataset not downloaded")

        dataset_path = Path(dataset.local_path)

        # Look for annotation files (common formats)
        annotation_paths = [
            dataset_path / annotations_file,
            dataset_path / "annotations" / annotations_file,
            dataset_path / "labels.json",
            dataset_path / "annotations" / "labels.json",
        ]

        annotation_file = None
        for path in annotation_paths:
            if path.exists():
                annotation_file = path
                break

        if not annotation_file:
            print("No annotation file found. Scanning for images...")
            return self._process_images_only(dataset, dataset_path)

        # Load annotations
        with open(annotation_file, 'r') as f:
            annotations_data = json.load(f)

        return self._process_annotations(dataset, dataset_path, annotations_data)

    def _process_images_only(self, dataset: Dataset, dataset_path: Path) -> int:
        """Process images without annotations"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff']
        image_files = []

        for ext in image_extensions:
            image_files.extend(dataset_path.rglob(f"*{ext}"))
            image_files.extend(dataset_path.rglob(f"*{ext.upper()}"))

        processed_count = 0
        for image_file in image_files:
            # Skip if already in database
            existing = self.db.query(Image).filter(
                Image.dataset_id == dataset.id,
                Image.filename == image_file.name
            ).first()

            if existing:
                continue

            # Read image to get dimensions
            img = cv2.imread(str(image_file))
            if img is None:
                continue

            height, width = img.shape[:2]

            # Create image record
            image = Image(
                dataset_id=dataset.id,
                filename=image_file.name,
                original_filename=image_file.name,
                file_path=str(image_file),
                image_type=ImageType.PANORAMIC,
                status=ImageStatus.UPLOADED,
                width=width,
                height=height,
                file_size=image_file.stat().st_size,
                is_annotated=False,
            )
            self.db.add(image)
            processed_count += 1

        self.db.commit()
        dataset.total_images = processed_count
        dataset.is_processed = True
        self.db.commit()

        return processed_count

    def _process_annotations(
        self,
        dataset: Dataset,
        dataset_path: Path,
        annotations_data: Dict
    ) -> int:
        """
        Process annotations in COCO or custom format

        Expected format variations:
        1. COCO format: {"images": [...], "annotations": [...], "categories": [...]}
        2. Custom format: {"image_name": {"regions": [...]}}
        """
        processed_count = 0

        # Detect format
        if "images" in annotations_data and "annotations" in annotations_data:
            # COCO format
            processed_count = self._process_coco_format(
                dataset, dataset_path, annotations_data
            )
        else:
            # Custom format
            processed_count = self._process_custom_format(
                dataset, dataset_path, annotations_data
            )

        dataset.total_images = processed_count
        dataset.is_processed = True
        self.db.commit()

        return processed_count

    def _process_coco_format(
        self,
        dataset: Dataset,
        dataset_path: Path,
        data: Dict
    ) -> int:
        """Process COCO format annotations"""
        images_data = {img["id"]: img for img in data["images"]}
        processed_count = 0

        for img_data in data["images"]:
            image_path = dataset_path / img_data["file_name"]
            if not image_path.exists():
                continue

            # Create image record
            image = Image(
                dataset_id=dataset.id,
                filename=img_data["file_name"],
                original_filename=img_data["file_name"],
                file_path=str(image_path),
                image_type=ImageType.PANORAMIC,
                status=ImageStatus.COMPLETED,
                width=img_data.get("width"),
                height=img_data.get("height"),
                file_size=image_path.stat().st_size,
                is_annotated=True,
            )
            self.db.add(image)
            self.db.flush()

            # Process annotations for this image
            img_annotations = [
                ann for ann in data["annotations"]
                if ann["image_id"] == img_data["id"]
            ]

            for ann in img_annotations:
                segmentation = ann.get("segmentation", [[]])
                if segmentation and len(segmentation[0]) > 0:
                    # Convert segmentation to polygon points
                    points = segmentation[0]
                    polygon = [[points[i], points[i+1]] for i in range(0, len(points), 2)]

                    annotation = Annotation(
                        image_id=image.id,
                        tooth_class=ann.get("category_id", 0),
                        polygon_points=polygon,
                        bbox=ann.get("bbox"),
                        area=ann.get("area"),
                    )
                    self.db.add(annotation)
                    image.annotation_count += 1

            processed_count += 1

        self.db.commit()
        return processed_count

    def _process_custom_format(
        self,
        dataset: Dataset,
        dataset_path: Path,
        data: Dict
    ) -> int:
        """Process custom format annotations"""
        processed_count = 0

        for image_name, image_data in data.items():
            image_path = dataset_path / image_name
            if not image_path.exists():
                # Try in subdirectories
                found_paths = list(dataset_path.rglob(image_name))
                if not found_paths:
                    continue
                image_path = found_paths[0]

            # Read image
            img = cv2.imread(str(image_path))
            if img is None:
                continue

            height, width = img.shape[:2]

            # Create image record
            image = Image(
                dataset_id=dataset.id,
                filename=image_name,
                original_filename=image_name,
                file_path=str(image_path),
                image_type=ImageType.PANORAMIC,
                status=ImageStatus.COMPLETED,
                width=width,
                height=height,
                file_size=image_path.stat().st_size,
                is_annotated=True,
            )
            self.db.add(image)
            self.db.flush()

            # Process regions/annotations
            regions = image_data.get("regions", [])
            for region in regions:
                # Extract polygon points
                if "shape_attributes" in region:
                    shape = region["shape_attributes"]
                    if shape.get("name") == "polygon":
                        x_points = shape.get("all_points_x", [])
                        y_points = shape.get("all_points_y", [])
                        polygon = [[x, y] for x, y in zip(x_points, y_points)]

                        # Get tooth class from region attributes
                        region_attrs = region.get("region_attributes", {})
                        tooth_class = int(region_attrs.get("tooth", 0))

                        annotation = Annotation(
                            image_id=image.id,
                            tooth_class=tooth_class,
                            polygon_points=polygon,
                        )
                        self.db.add(annotation)
                        image.annotation_count += 1

            processed_count += 1

        self.db.commit()
        return processed_count

    def get_dataset_stats(self, dataset: Dataset) -> Dict:
        """Get statistics for a dataset"""
        total_images = self.db.query(Image).filter(
            Image.dataset_id == dataset.id
        ).count()

        total_annotations = self.db.query(Annotation).join(Image).filter(
            Image.dataset_id == dataset.id
        ).count()

        return {
            "name": dataset.name,
            "kaggle_path": dataset.kaggle_path,
            "total_images": total_images,
            "total_annotations": total_annotations,
            "is_downloaded": dataset.is_downloaded,
            "is_processed": dataset.is_processed,
            "local_path": dataset.local_path,
        }
