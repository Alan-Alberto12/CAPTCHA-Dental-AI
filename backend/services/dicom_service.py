"""
DICOM Image Processing Service

Handles DICOM file processing, conversion, and metadata extraction for dental radiography.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
import pydicom
from pydicom.dataset import FileDataset
import numpy as np
import cv2
from PIL import Image as PILImage
from sqlalchemy.orm import Session
from models.image import Image, ImageType, ImageStatus


class DICOMService:
    """Service for handling DICOM files in dental imaging"""

    def __init__(self, db: Session, upload_dir: str = "./uploads"):
        self.db = db
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.dicom_dir = self.upload_dir / "dicom"
        self.dicom_dir.mkdir(parents=True, exist_ok=True)
        self.converted_dir = self.upload_dir / "converted"
        self.converted_dir.mkdir(parents=True, exist_ok=True)

    def is_dicom_file(self, file_path: str) -> bool:
        """
        Check if a file is a valid DICOM file

        Args:
            file_path: Path to the file

        Returns:
            True if valid DICOM, False otherwise
        """
        try:
            pydicom.dcmread(file_path, stop_before_pixels=True)
            return True
        except Exception:
            return False

    def read_dicom(self, file_path: str) -> Optional[FileDataset]:
        """
        Read a DICOM file

        Args:
            file_path: Path to DICOM file

        Returns:
            DICOM dataset or None if invalid
        """
        try:
            dicom_data = pydicom.dcmread(file_path)
            return dicom_data
        except Exception as e:
            print(f"Error reading DICOM file: {e}")
            return None

    def extract_metadata(self, dicom_data: FileDataset) -> Dict:
        """
        Extract metadata from DICOM file

        Args:
            dicom_data: DICOM dataset

        Returns:
            Dictionary of metadata
        """
        metadata = {}

        # Patient information
        metadata["patient_id"] = str(getattr(dicom_data, "PatientID", "Unknown"))
        metadata["patient_name"] = str(getattr(dicom_data, "PatientName", "Unknown"))
        metadata["patient_birth_date"] = str(getattr(dicom_data, "PatientBirthDate", ""))
        metadata["patient_sex"] = str(getattr(dicom_data, "PatientSex", ""))

        # Study information
        metadata["study_date"] = str(getattr(dicom_data, "StudyDate", ""))
        metadata["study_time"] = str(getattr(dicom_data, "StudyTime", ""))
        metadata["study_description"] = str(getattr(dicom_data, "StudyDescription", ""))
        metadata["study_instance_uid"] = str(getattr(dicom_data, "StudyInstanceUID", ""))

        # Series information
        metadata["series_description"] = str(getattr(dicom_data, "SeriesDescription", ""))
        metadata["series_number"] = str(getattr(dicom_data, "SeriesNumber", ""))
        metadata["modality"] = str(getattr(dicom_data, "Modality", ""))

        # Image information
        metadata["rows"] = int(getattr(dicom_data, "Rows", 0))
        metadata["columns"] = int(getattr(dicom_data, "Columns", 0))
        metadata["bits_allocated"] = int(getattr(dicom_data, "BitsAllocated", 0))
        metadata["bits_stored"] = int(getattr(dicom_data, "BitsStored", 0))
        metadata["photometric_interpretation"] = str(
            getattr(dicom_data, "PhotometricInterpretation", "")
        )

        # Pixel spacing
        if hasattr(dicom_data, "PixelSpacing"):
            metadata["pixel_spacing"] = [float(x) for x in dicom_data.PixelSpacing]

        # Institution info
        metadata["institution_name"] = str(getattr(dicom_data, "InstitutionName", ""))
        metadata["manufacturer"] = str(getattr(dicom_data, "Manufacturer", ""))
        metadata["manufacturer_model"] = str(getattr(dicom_data, "ManufacturerModelName", ""))

        return metadata

    def dicom_to_image(
        self,
        dicom_data: FileDataset,
        output_format: str = "png",
        apply_window: bool = True,
        window_center: Optional[int] = None,
        window_width: Optional[int] = None,
    ) -> np.ndarray:
        """
        Convert DICOM pixel data to image array

        Args:
            dicom_data: DICOM dataset
            output_format: Output format (png, jpg)
            apply_window: Whether to apply windowing
            window_center: Window center value
            window_width: Window width value

        Returns:
            Image array (numpy)
        """
        # Get pixel array
        pixel_array = dicom_data.pixel_array.astype(float)

        # Apply rescale slope and intercept if available
        if hasattr(dicom_data, "RescaleSlope") and hasattr(dicom_data, "RescaleIntercept"):
            pixel_array = pixel_array * dicom_data.RescaleSlope + dicom_data.RescaleIntercept

        # Apply windowing for better visualization
        if apply_window:
            if window_center is None:
                window_center = getattr(dicom_data, "WindowCenter", None)
                if isinstance(window_center, pydicom.multival.MultiValue):
                    window_center = float(window_center[0])
                elif window_center:
                    window_center = float(window_center)
                else:
                    window_center = pixel_array.mean()

            if window_width is None:
                window_width = getattr(dicom_data, "WindowWidth", None)
                if isinstance(window_width, pydicom.multival.MultiValue):
                    window_width = float(window_width[0])
                elif window_width:
                    window_width = float(window_width)
                else:
                    window_width = pixel_array.std() * 2

            lower = window_center - window_width / 2
            upper = window_center + window_width / 2
            pixel_array = np.clip(pixel_array, lower, upper)

        # Normalize to 0-255
        pixel_array = pixel_array - pixel_array.min()
        pixel_array = pixel_array / pixel_array.max()
        pixel_array = (pixel_array * 255).astype(np.uint8)

        # Handle photometric interpretation
        if hasattr(dicom_data, "PhotometricInterpretation"):
            if dicom_data.PhotometricInterpretation == "MONOCHROME1":
                pixel_array = 255 - pixel_array  # Invert

        return pixel_array

    def save_dicom_as_image(
        self,
        dicom_data: FileDataset,
        output_path: str,
        output_format: str = "png",
    ) -> str:
        """
        Save DICOM as standard image format

        Args:
            dicom_data: DICOM dataset
            output_path: Output file path
            output_format: Output format (png, jpg)

        Returns:
            Path to saved image
        """
        image_array = self.dicom_to_image(dicom_data, output_format)

        # Save using PIL
        image = PILImage.fromarray(image_array)
        image.save(output_path, format=output_format.upper())

        return output_path

    def process_dicom_upload(
        self,
        dicom_file_path: str,
        user_id: Optional[int] = None,
        convert_to_png: bool = True,
    ) -> Tuple[Image, str]:
        """
        Process an uploaded DICOM file

        Args:
            dicom_file_path: Path to uploaded DICOM file
            user_id: ID of user who uploaded
            convert_to_png: Whether to convert to PNG

        Returns:
            Tuple of (Image object, converted image path)
        """
        # Read DICOM
        dicom_data = self.read_dicom(dicom_file_path)
        if not dicom_data:
            raise ValueError("Invalid DICOM file")

        # Extract metadata
        metadata = self.extract_metadata(dicom_data)

        # Save DICOM to permanent location
        filename = Path(dicom_file_path).name
        permanent_dicom_path = self.dicom_dir / filename
        os.rename(dicom_file_path, permanent_dicom_path)

        # Convert to PNG if requested
        converted_path = None
        if convert_to_png:
            png_filename = Path(filename).stem + ".png"
            converted_path = self.converted_dir / png_filename
            self.save_dicom_as_image(dicom_data, str(converted_path))

        # Parse study date
        study_date = None
        if metadata.get("study_date"):
            try:
                study_date = datetime.strptime(metadata["study_date"], "%Y%m%d")
            except ValueError:
                pass

        # Create Image record
        image = Image(
            user_id=user_id,
            filename=filename,
            original_filename=filename,
            file_path=str(converted_path) if converted_path else str(permanent_dicom_path),
            dicom_path=str(permanent_dicom_path),
            image_type=ImageType.DICOM,
            status=ImageStatus.COMPLETED,
            width=metadata.get("columns"),
            height=metadata.get("rows"),
            file_size=os.path.getsize(permanent_dicom_path),
            dicom_metadata=metadata,
            patient_id=metadata.get("patient_id"),
            study_date=study_date,
        )

        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)

        return image, str(converted_path) if converted_path else str(permanent_dicom_path)

    def anonymize_dicom(self, dicom_data: FileDataset) -> FileDataset:
        """
        Anonymize DICOM file by removing patient information

        Args:
            dicom_data: DICOM dataset

        Returns:
            Anonymized DICOM dataset
        """
        # Tags to anonymize
        tags_to_remove = [
            "PatientName",
            "PatientID",
            "PatientBirthDate",
            "PatientSex",
            "PatientAge",
            "PatientWeight",
            "PatientAddress",
            "InstitutionName",
            "InstitutionAddress",
            "ReferringPhysicianName",
            "PerformingPhysicianName",
        ]

        for tag in tags_to_remove:
            if hasattr(dicom_data, tag):
                setattr(dicom_data, tag, "ANONYMIZED")

        return dicom_data

    def batch_convert_dicom_directory(
        self,
        input_dir: str,
        output_format: str = "png",
    ) -> int:
        """
        Convert all DICOM files in a directory to image format

        Args:
            input_dir: Directory containing DICOM files
            output_format: Output format

        Returns:
            Number of files converted
        """
        input_path = Path(input_dir)
        converted_count = 0

        for dicom_file in input_path.rglob("*.dcm"):
            try:
                dicom_data = self.read_dicom(str(dicom_file))
                if dicom_data:
                    output_filename = dicom_file.stem + f".{output_format}"
                    output_path = self.converted_dir / output_filename
                    self.save_dicom_as_image(dicom_data, str(output_path), output_format)
                    converted_count += 1
            except Exception as e:
                print(f"Error converting {dicom_file}: {e}")
                continue

        return converted_count
