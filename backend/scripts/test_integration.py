"""
Test script to verify the teeth segmentation integration is working

This script tests:
1. Database models
2. Kaggle service
3. DICOM service
4. Segmentation service
5. API endpoints (basic)

Usage:
    python scripts/test_integration.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database import SessionLocal, engine, Base
from models import (
    User, Dataset, Image, Annotation, Prediction, SegmentationModel,
    ImageType, ImageStatus
)


def test_database_models():
    """Test that all database models are properly created"""
    print("\n" + "=" * 60)
    print("TEST 1: Database Models")
    print("=" * 60)

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ All database tables created successfully")

        # Test query on each table
        db = SessionLocal()

        tables = {
            "users": User,
            "datasets": Dataset,
            "images": Image,
            "annotations": Annotation,
            "predictions": Prediction,
            "segmentation_models": SegmentationModel,
        }

        for table_name, model in tables.items():
            count = db.query(model).count()
            print(f"✓ Table '{table_name}': {count} records")

        db.close()
        print("\n✅ Database models test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Database models test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_services_import():
    """Test that all services can be imported"""
    print("\n" + "=" * 60)
    print("TEST 2: Service Imports")
    print("=" * 60)

    try:
        from services.kaggle_service import KaggleDatasetService
        print("✓ KaggleDatasetService imported")

        from services.dicom_service import DICOMService
        print("✓ DICOMService imported")

        from services.segmentation_service import SegmentationService, UNet
        print("✓ SegmentationService imported")
        print("✓ UNet model imported")

        print("\n✅ Service imports test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Service imports test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_kaggle_service():
    """Test Kaggle service initialization"""
    print("\n" + "=" * 60)
    print("TEST 3: Kaggle Service")
    print("=" * 60)

    try:
        from services.kaggle_service import KaggleDatasetService

        db = SessionLocal()
        service = KaggleDatasetService(db)

        print("✓ KaggleDatasetService initialized")
        print(f"✓ Data directory: {service.data_dir}")

        # Check if data directory was created
        if service.data_dir.exists():
            print(f"✓ Data directory exists: {service.data_dir}")
        else:
            print(f"⚠ Data directory not found (will be created on first use)")

        db.close()
        print("\n✅ Kaggle service test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Kaggle service test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dicom_service():
    """Test DICOM service initialization"""
    print("\n" + "=" * 60)
    print("TEST 4: DICOM Service")
    print("=" * 60)

    try:
        from services.dicom_service import DICOMService

        db = SessionLocal()
        service = DICOMService(db)

        print("✓ DICOMService initialized")
        print(f"✓ Upload directory: {service.upload_dir}")
        print(f"✓ DICOM directory: {service.dicom_dir}")
        print(f"✓ Converted directory: {service.converted_dir}")

        # Check directories
        if service.upload_dir.exists():
            print(f"✓ Upload directory exists")
        if service.dicom_dir.exists():
            print(f"✓ DICOM directory exists")
        if service.converted_dir.exists():
            print(f"✓ Converted directory exists")

        db.close()
        print("\n✅ DICOM service test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ DICOM service test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_segmentation_service():
    """Test Segmentation service and model"""
    print("\n" + "=" * 60)
    print("TEST 5: Segmentation Service")
    print("=" * 60)

    try:
        from services.segmentation_service import SegmentationService, UNet
        import torch

        db = SessionLocal()
        service = SegmentationService(db)

        print("✓ SegmentationService initialized")
        print(f"✓ Model directory: {service.model_dir}")
        print(f"✓ Device: {service.device}")

        # Test U-Net model
        model = UNet(in_channels=1, num_classes=32)
        print("✓ U-Net model created")

        # Test forward pass with dummy data
        dummy_input = torch.randn(1, 1, 512, 512)
        with torch.no_grad():
            output = model(dummy_input)

        print(f"✓ Model forward pass successful")
        print(f"✓ Input shape: {dummy_input.shape}")
        print(f"✓ Output shape: {output.shape}")

        db.close()
        print("\n✅ Segmentation service test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Segmentation service test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_routes():
    """Test that API routes can be imported"""
    print("\n" + "=" * 60)
    print("TEST 6: API Routes")
    print("=" * 60)

    try:
        from api.routes import dataset, images, predictions

        print("✓ Dataset routes imported")
        print(f"  - Router prefix: {dataset.router.prefix}")
        print(f"  - Routes: {len(dataset.router.routes)}")

        print("✓ Images routes imported")
        print(f"  - Router prefix: {images.router.prefix}")
        print(f"  - Routes: {len(images.router.routes)}")

        print("✓ Predictions routes imported")
        print(f"  - Router prefix: {predictions.router.prefix}")
        print(f"  - Routes: {len(predictions.router.routes)}")

        print("\n✅ API routes test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ API routes test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """Test that all required dependencies are installed"""
    print("\n" + "=" * 60)
    print("TEST 7: Dependencies")
    print("=" * 60)

    dependencies = {
        "torch": "PyTorch",
        "torchvision": "TorchVision",
        "cv2": "OpenCV",
        "PIL": "Pillow",
        "numpy": "NumPy",
        "pydicom": "pydicom",
        "kagglehub": "Kaggle Hub",
        "albumentations": "Albumentations",
        "sklearn": "scikit-learn",
    }

    all_installed = True

    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} NOT installed")
            all_installed = False

    if all_installed:
        print("\n✅ All dependencies installed")
        return True
    else:
        print("\n⚠ Some dependencies missing - run: pip install -r requirements.txt")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("TEETH SEGMENTATION INTEGRATION TEST SUITE")
    print("=" * 60)

    results = {
        "Database Models": test_database_models(),
        "Service Imports": test_services_import(),
        "Kaggle Service": test_kaggle_service(),
        "DICOM Service": test_dicom_service(),
        "Segmentation Service": test_segmentation_service(),
        "API Routes": test_api_routes(),
        "Dependencies": test_dependencies(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! The integration is working correctly.")
        print("\nNext steps:")
        print("1. Configure Kaggle API: ~/.kaggle/kaggle.json")
        print("2. Download dataset: python scripts/download_kaggle_dataset.py")
        print("3. Start the server: uvicorn main:app --reload")
        print("4. Test the API endpoints")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Check database connection")
        print("3. Verify all files were created correctly")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
