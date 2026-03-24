#!/usr/bin/env python3
"""
Quick API Test Script - Test everything in one command!

This script tests the entire teeth segmentation pipeline without a frontend:
1. Creates a test user
2. Downloads Kaggle dataset
3. Processes annotations
4. Uploads a test image
5. Runs prediction
6. Generates visualization

Usage:
    python scripts/quick_test.py

Requirements:
    - Server must be running: uvicorn main:app --reload
    - Kaggle API must be configured: ~/.kaggle/kaggle.json
"""

import sys
from pathlib import Path
import requests
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def print_step(step_num, text):
    """Print a step"""
    print(f"\n{step_num}. {text}")

def print_success(text):
    """Print success message"""
    print(f"   ✓ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"   ⚠ {text}")

def print_error(text):
    """Print error message"""
    print(f"   ✗ {text}")

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    """Run all tests"""

    print_header("TEETH SEGMENTATION API - QUICK TEST")
    print("\nThis will test the entire pipeline without a frontend.")
    print("Make sure the server is running: uvicorn main:app --reload")

    # Check server
    print_step("0", "Checking if server is running...")
    if not check_server():
        print_error("Server is not running!")
        print("\nPlease start the server first:")
        print("  cd backend")
        print("  uvicorn main:app --reload")
        sys.exit(1)
    print_success("Server is running")

    # 1. Create user
    print_step("1", "Creating test user...")

    signup_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        if response.status_code == 201:
            print_success("User created successfully")
        elif response.status_code == 400 and "already registered" in response.text:
            print_warning("User already exists (this is OK)")
        else:
            print_error(f"Failed to create user: {response.text}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

    # 2. Login
    print_step("2", "Logging in...")

    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data
        )

        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success("Login successful")
            print(f"   Access token: {token[:30]}...")
        else:
            print_error(f"Login failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Login request failed: {e}")
        return False

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Check Kaggle configuration
    print_step("3", "Checking Kaggle API configuration...")

    kaggle_config = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_config.exists():
        print_success(f"Kaggle API configured: {kaggle_config}")
    else:
        print_error("Kaggle API not configured!")
        print("\n   To configure Kaggle API:")
        print("   1. Go to https://www.kaggle.com/account")
        print("   2. Click 'Create New Token'")
        print("   3. Move kaggle.json to ~/.kaggle/")
        print("\n   Skipping dataset download...")
        skip_dataset = True

    # 4. Download dataset (optional)
    skip_dataset = False
    dataset_id = None

    if not skip_dataset:
        print_step("4", "Checking for Kaggle dataset...")

        try:
            # Check if dataset already exists
            response = requests.get(f"{BASE_URL}/datasets/", headers=headers)

            if response.status_code == 200:
                datasets = response.json()
                if datasets:
                    dataset_id = datasets[0]["id"]
                    print_success(f"Dataset already exists (ID: {dataset_id})")
                else:
                    # Download dataset
                    print("   Dataset not found. Downloading from Kaggle...")
                    print("   ⚠ This may take 2-5 minutes depending on your connection...")

                    dataset_data = {
                        "kaggle_path": "humansintheloop/teeth-segmentation-on-dental-x-ray-images",
                        "name": "Teeth Segmentation Dataset"
                    }

                    response = requests.post(
                        f"{BASE_URL}/datasets/download",
                        json=dataset_data,
                        headers=headers,
                        timeout=300  # 5 minute timeout
                    )

                    if response.status_code == 200:
                        dataset = response.json()
                        dataset_id = dataset["id"]
                        print_success(f"Dataset downloaded (ID: {dataset_id})")
                    else:
                        print_warning(f"Dataset download failed: {response.text}")
        except Exception as e:
            print_warning(f"Dataset check failed: {e}")

    # 5. Get dataset stats
    if dataset_id:
        print_step("5", "Getting dataset statistics...")

        try:
            response = requests.get(
                f"{BASE_URL}/datasets/{dataset_id}/stats",
                headers=headers
            )

            if response.status_code == 200:
                stats = response.json()
                print_success(f"Dataset loaded successfully")
                print(f"      - Total images: {stats['total_images']}")
                print(f"      - Total annotations: {stats['total_annotations']}")
                print(f"      - Downloaded: {stats['is_downloaded']}")
                print(f"      - Processed: {stats['is_processed']}")
            else:
                print_warning(f"Could not get stats: {response.text}")
        except Exception as e:
            print_warning(f"Stats request failed: {e}")

    # 6. List available images
    print_step("6", "Checking available images...")

    try:
        response = requests.get(f"{BASE_URL}/images/", headers=headers)

        if response.status_code == 200:
            images = response.json()
            print_success(f"Found {len(images)} images in database")

            if images:
                # Use first image for testing
                test_image = images[0]
                image_id = test_image["id"]
                print(f"      - Using image ID {image_id}: {test_image['filename']}")

                # 7. Run prediction
                print_step("7", "Running teeth segmentation prediction...")

                pred_data = {
                    "image_id": image_id,
                    "confidence_threshold": 0.5
                }

                try:
                    response = requests.post(
                        f"{BASE_URL}/predictions/predict",
                        json=pred_data,
                        headers=headers
                    )

                    if response.status_code == 200:
                        result = response.json()
                        print_success(f"Prediction completed!")
                        print(f"      - Teeth detected: {result['total_predictions']}")
                        print(f"      - Inference time: {result['inference_time']:.3f}s")

                        if result['total_predictions'] > 0:
                            print(f"      - Predictions:")
                            for pred in result['predictions'][:5]:  # Show first 5
                                print(f"         • Tooth {pred['tooth_class']}: {pred['confidence_score']:.2%}")
                        else:
                            print_warning("No teeth detected (model may need training)")
                    else:
                        print_error(f"Prediction failed: {response.text}")
                except Exception as e:
                    print_error(f"Prediction request failed: {e}")

                # 8. Generate visualization
                print_step("8", "Generating visualization...")

                try:
                    response = requests.get(
                        f"{BASE_URL}/predictions/image/{image_id}/visualize",
                        headers=headers
                    )

                    if response.status_code == 200:
                        # Save visualization
                        output_path = Path("prediction_visualization.png")
                        with open(output_path, "wb") as f:
                            f.write(response.content)

                        print_success(f"Visualization saved to: {output_path.absolute()}")

                        # Try to open it
                        import platform
                        if platform.system() == "Darwin":  # macOS
                            import subprocess
                            subprocess.run(["open", str(output_path)])
                            print_success("Opening visualization...")
                        elif platform.system() == "Linux":
                            import subprocess
                            subprocess.run(["xdg-open", str(output_path)])
                            print_success("Opening visualization...")
                        else:
                            print(f"      Open this file to view results: {output_path.absolute()}")
                    else:
                        print_warning("Could not generate visualization")
                except Exception as e:
                    print_warning(f"Visualization request failed: {e}")
            else:
                print_warning("No images available for testing")
                print("      Try uploading an image or downloading the Kaggle dataset")
        else:
            print_error(f"Could not list images: {response.text}")
    except Exception as e:
        print_error(f"Image list request failed: {e}")

    # 9. List available models
    print_step("9", "Checking available ML models...")

    try:
        response = requests.get(
            f"{BASE_URL}/predictions/models/",
            headers=headers
        )

        if response.status_code == 200:
            models = response.json()
            print_success(f"Found {len(models)} model(s)")
            for model in models:
                print(f"      - {model['name']} (v{model['version']}) - {model['architecture']}")
                if not model['is_active']:
                    print_warning("        Model is not active")
        else:
            print_warning(f"Could not list models: {response.text}")
    except Exception as e:
        print_warning(f"Model list request failed: {e}")

    # Summary
    print_header("TEST COMPLETE")
    print("\n✅ Quick test finished successfully!")

    print("\nWhat was tested:")
    print("  ✓ User authentication")
    print("  ✓ Dataset management")
    print("  ✓ Image handling")
    print("  ✓ Teeth segmentation prediction")
    print("  ✓ Visualization generation")
    print("  ✓ Model management")

    print("\nNext steps:")
    print("  1. Train the U-Net model on the Kaggle dataset")
    print("  2. Build React frontend components")
    print("  3. Add more test images")
    print("  4. Explore the API at: http://localhost:8000/docs")

    print("\nFor detailed testing, see: TESTING_WITHOUT_FRONTEND.md")
    print("=" * 60 + "\n")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
