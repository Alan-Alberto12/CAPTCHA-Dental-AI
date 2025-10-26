# Testing Teeth Segmentation Without Frontend

This guide shows you how to test all functionality without building a frontend.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Method 1: Run Test Suite](#method-1-run-test-suite)
3. [Method 2: Swagger UI (Interactive API)](#method-2-swagger-ui-interactive-api)
4. [Method 3: cURL Commands](#method-3-curl-commands)
5. [Method 4: Python Scripts](#method-4-python-scripts)
6. [Method 5: Postman/Insomnia](#method-5-postmaninsomnia)

---

## Prerequisites

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Kaggle API
```bash
# Download kaggle.json from https://www.kaggle.com/account
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 3. Start Database
```bash
docker-compose up -d
```

### 4. Start Backend Server
```bash
cd backend
uvicorn main:app --reload
```

Server will be at: **http://localhost:8000**

---

## Method 1: Run Test Suite ⭐ RECOMMENDED

This is the **easiest and fastest** way to verify everything works!

```bash
cd backend
python scripts/test_integration.py
```

**Expected Output:**
```
============================================================
TEETH SEGMENTATION INTEGRATION TEST SUITE
============================================================

============================================================
TEST 1: Database Models
============================================================
✓ All database tables created successfully
✓ Table 'users': 0 records
✓ Table 'datasets': 0 records
✓ Table 'images': 0 records
✓ Table 'annotations': 0 records
✓ Table 'predictions': 0 records
✓ Table 'segmentation_models': 0 records

✅ Database models test PASSED

... (more tests)

============================================================
TEST SUMMARY
============================================================
Database Models................................ ✅ PASSED
Service Imports................................ ✅ PASSED
Kaggle Service................................. ✅ PASSED
DICOM Service.................................. ✅ PASSED
Segmentation Service........................... ✅ PASSED
API Routes..................................... ✅ PASSED
Dependencies................................... ✅ PASSED

Total: 7/7 tests passed

🎉 All tests passed! The integration is working correctly.
```

---

## Method 2: Swagger UI (Interactive API) ⭐ EASIEST

FastAPI provides an **interactive web interface** for testing APIs!

### Access Swagger UI
Open in your browser:
```
http://localhost:8000/docs
```

### Step-by-Step Testing

#### 1. **Create a User**
- Click on `POST /auth/signup`
- Click "Try it out"
- Fill in the request body:
```json
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "testpass123",
  "first_name": "Test",
  "last_name": "User"
}
```
- Click "Execute"
- You should see a 201 response with user data

#### 2. **Login**
- Click on `POST /auth/login`
- Click "Try it out"
- Fill in:
  - username: `testuser`
  - password: `testpass123`
- Click "Execute"
- **Copy the `access_token`** from the response

#### 3. **Authorize**
- Click the "Authorize" button at the top
- Paste your token
- Click "Authorize"
- Now all requests will include your token!

#### 4. **Download Dataset**
- Click on `POST /datasets/download`
- Click "Try it out"
- Fill in:
```json
{
  "kaggle_path": "humansintheloop/teeth-segmentation-on-dental-x-ray-images",
  "name": "Teeth Segmentation Dataset"
}
```
- Click "Execute"
- Wait 2-5 minutes for download
- You'll see the dataset ID in the response

#### 5. **Get Dataset Stats**
- Click on `GET /datasets/{dataset_id}/stats`
- Enter the dataset_id from previous step
- Click "Execute"
- You'll see total images and annotations

#### 6. **Upload an Image**
- Click on `POST /images/upload`
- Click "Try it out"
- Upload a PNG/JPG dental X-ray
- Set image_type: "panoramic"
- Click "Execute"
- Note the `image.id` from response

#### 7. **Run Prediction**
- Click on `POST /predictions/predict`
- Click "Try it out"
- Fill in:
```json
{
  "image_id": 1,
  "confidence_threshold": 0.5
}
```
- Click "Execute"
- You'll see predicted teeth!

#### 8. **Visualize Results**
- Click on `GET /predictions/image/{image_id}/visualize`
- Enter your image_id
- Click "Execute"
- Click "Download file" to see the visualization

---

## Method 3: cURL Commands

### Setup: Get Access Token
```bash
# Create user
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"

# Save the access_token from response
export TOKEN="your_access_token_here"
```

### Test 1: Download Kaggle Dataset
```bash
curl -X POST "http://localhost:8000/datasets/download" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "kaggle_path": "humansintheloop/teeth-segmentation-on-dental-x-ray-images",
    "name": "Teeth Segmentation Dataset"
  }'
```

### Test 2: List Datasets
```bash
curl -X GET "http://localhost:8000/datasets/" \
  -H "Authorization: Bearer $TOKEN"
```

### Test 3: Get Dataset Stats
```bash
# Replace {dataset_id} with actual ID from previous command
curl -X GET "http://localhost:8000/datasets/1/stats" \
  -H "Authorization: Bearer $TOKEN"
```

### Test 4: Upload Image
```bash
curl -X POST "http://localhost:8000/images/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/dental_xray.png" \
  -F "image_type=panoramic"
```

### Test 5: Upload DICOM
```bash
curl -X POST "http://localhost:8000/images/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/dental_scan.dcm" \
  -F "image_type=dicom" \
  -F "convert_dicom=true"
```

### Test 6: List Images
```bash
curl -X GET "http://localhost:8000/images/" \
  -H "Authorization: Bearer $TOKEN"
```

### Test 7: Run Prediction
```bash
curl -X POST "http://localhost:8000/predictions/predict" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 1,
    "confidence_threshold": 0.5
  }'
```

### Test 8: Get Predictions
```bash
curl -X GET "http://localhost:8000/predictions/image/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Test 9: Download Visualization
```bash
curl -X GET "http://localhost:8000/predictions/image/1/visualize" \
  -H "Authorization: Bearer $TOKEN" \
  -o result.png

# Open the image
open result.png  # macOS
xdg-open result.png  # Linux
```

### Test 10: List Models
```bash
curl -X GET "http://localhost:8000/predictions/models/" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Method 4: Python Scripts

### Complete Test Script

Save as `test_api.py`:

```python
#!/usr/bin/env python3
"""
Complete API test script
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    """Test the complete workflow"""

    print("=" * 60)
    print("TESTING TEETH SEGMENTATION API")
    print("=" * 60)

    # 1. Create user
    print("\n1. Creating user...")
    signup_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }

    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    if response.status_code == 201:
        print("   ✓ User created")
    elif response.status_code == 400:
        print("   ⚠ User already exists (OK)")
    else:
        print(f"   ✗ Failed: {response.text}")
        return

    # 2. Login
    print("\n2. Logging in...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }

    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        print("   ✓ Login successful")
        print(f"   Token: {token[:20]}...")
    else:
        print(f"   ✗ Failed: {response.text}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Download dataset
    print("\n3. Downloading Kaggle dataset...")
    print("   (This may take 2-5 minutes...)")

    dataset_data = {
        "kaggle_path": "humansintheloop/teeth-segmentation-on-dental-x-ray-images",
        "name": "Teeth Segmentation Dataset"
    }

    response = requests.post(
        f"{BASE_URL}/datasets/download",
        json=dataset_data,
        headers=headers
    )

    if response.status_code == 200:
        dataset = response.json()
        dataset_id = dataset["id"]
        print(f"   ✓ Dataset downloaded (ID: {dataset_id})")
    else:
        print(f"   ⚠ Download failed or already exists: {response.text}")
        dataset_id = 1  # Try with existing dataset

    # 4. Get dataset stats
    print("\n4. Getting dataset statistics...")

    response = requests.get(
        f"{BASE_URL}/datasets/{dataset_id}/stats",
        headers=headers
    )

    if response.status_code == 200:
        stats = response.json()
        print(f"   ✓ Total images: {stats['total_images']}")
        print(f"   ✓ Total annotations: {stats['total_annotations']}")
    else:
        print(f"   ✗ Failed: {response.text}")

    # 5. List images
    print("\n5. Listing images...")

    response = requests.get(
        f"{BASE_URL}/images/",
        headers=headers
    )

    if response.status_code == 200:
        images = response.json()
        print(f"   ✓ Found {len(images)} images")

        if images:
            image_id = images[0]["id"]
            print(f"   Using image ID: {image_id}")

            # 6. Run prediction
            print("\n6. Running prediction...")

            pred_data = {
                "image_id": image_id,
                "confidence_threshold": 0.5
            }

            response = requests.post(
                f"{BASE_URL}/predictions/predict",
                json=pred_data,
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ Found {result['total_predictions']} teeth")
                print(f"   ✓ Inference time: {result['inference_time']:.3f}s")
            else:
                print(f"   ✗ Failed: {response.text}")

            # 7. Get visualization
            print("\n7. Downloading visualization...")

            response = requests.get(
                f"{BASE_URL}/predictions/image/{image_id}/visualize",
                headers=headers
            )

            if response.status_code == 200:
                output_path = "prediction_result.png"
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"   ✓ Saved to: {output_path}")
            else:
                print(f"   ⚠ No visualization available")
    else:
        print(f"   ✗ Failed: {response.text}")

    # 8. List models
    print("\n8. Listing available models...")

    response = requests.get(
        f"{BASE_URL}/predictions/models/",
        headers=headers
    )

    if response.status_code == 200:
        models = response.json()
        print(f"   ✓ Found {len(models)} model(s)")
        for model in models:
            print(f"      - {model['name']} (v{model['version']})")
    else:
        print(f"   ✗ Failed: {response.text}")

    print("\n" + "=" * 60)
    print("✅ Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_complete_workflow()
```

**Run it:**
```bash
python test_api.py
```

### Quick Download Test

```python
import kagglehub

# Download dataset
path = kagglehub.dataset_download("humansintheloop/teeth-segmentation-on-dental-x-ray-images")
print("Path to dataset files:", path)
```

### Test DICOM Processing

```python
from services.database import SessionLocal
from services.dicom_service import DICOMService

db = SessionLocal()
service = DICOMService(db)

# Test with a DICOM file
image, png_path = service.process_dicom_upload(
    dicom_file_path="path/to/your.dcm",
    user_id=1,
    convert_to_png=True
)

print(f"Image ID: {image.id}")
print(f"Converted to: {png_path}")
print(f"Metadata: {image.dicom_metadata}")
```

### Test Segmentation

```python
from services.database import SessionLocal
from services.segmentation_service import SegmentationService

db = SessionLocal()
service = SegmentationService(db)

# Run prediction
predictions = service.predict(
    image_id=1,
    confidence_threshold=0.5
)

print(f"Found {len(predictions)} teeth")
for pred in predictions:
    print(f"  Tooth {pred.tooth_class}: {pred.confidence_score:.2%}")
```

---

## Method 5: Postman/Insomnia

### Import this collection

Save as `postman_collection.json`:

```json
{
  "info": {
    "name": "Teeth Segmentation API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Signup",
          "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "url": "{{base_url}}/auth/signup",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"username\": \"testuser\",\n  \"password\": \"testpass123\",\n  \"first_name\": \"Test\",\n  \"last_name\": \"User\"\n}"
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [],
            "url": "{{base_url}}/auth/login",
            "body": {
              "mode": "urlencoded",
              "urlencoded": [
                {"key": "username", "value": "testuser"},
                {"key": "password", "value": "testpass123"}
              ]
            }
          }
        }
      ]
    },
    {
      "name": "Datasets",
      "item": [
        {
          "name": "Download Dataset",
          "request": {
            "method": "POST",
            "header": [
              {"key": "Authorization", "value": "Bearer {{token}}"},
              {"key": "Content-Type", "value": "application/json"}
            ],
            "url": "{{base_url}}/datasets/download",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"kaggle_path\": \"humansintheloop/teeth-segmentation-on-dental-x-ray-images\"\n}"
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {"key": "base_url", "value": "http://localhost:8000"},
    {"key": "token", "value": ""}
  ]
}
```

Import into Postman and test!

---

## Quick Verification Checklist

Run these commands in order:

```bash
# 1. Test imports
cd backend
python -c "from services.kaggle_service import KaggleDatasetService; print('✓ Kaggle service OK')"
python -c "from services.dicom_service import DICOMService; print('✓ DICOM service OK')"
python -c "from services.segmentation_service import SegmentationService; print('✓ Segmentation service OK')"

# 2. Run full test suite
python scripts/test_integration.py

# 3. Start server
uvicorn main:app --reload &

# 4. Test health endpoint
curl http://localhost:8000/health

# 5. Open Swagger UI
open http://localhost:8000/docs  # macOS
xdg-open http://localhost:8000/docs  # Linux

# 6. Download dataset
python scripts/download_kaggle_dataset.py
```

---

## Expected Results

### ✅ Success Indicators

1. **Test suite**: All 7 tests pass
2. **Swagger UI**: Loads at http://localhost:8000/docs
3. **Dataset download**: ~598 images downloaded
4. **Image upload**: Returns image ID
5. **Prediction**: Returns list of teeth
6. **Visualization**: PNG file generated

### ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: torch` | Run `pip install -r requirements.txt` |
| `Kaggle API credentials not found` | Configure `~/.kaggle/kaggle.json` |
| `Database connection failed` | Start PostgreSQL: `docker-compose up -d` |
| `Predictions are random` | Expected! Model is untrained. You need to train it first. |

---

## Summary

**Recommended Testing Order:**

1. ✅ **Run test suite** - Fastest verification
2. ✅ **Use Swagger UI** - Most visual and interactive
3. ✅ **Download dataset** - Get real data
4. ✅ **Try cURL commands** - Test specific endpoints
5. ✅ **Run Python scripts** - Automation

**No frontend needed!** Everything can be tested through:
- Automated test scripts
- Swagger UI (built-in web interface)
- cURL commands
- Python scripts
- Postman/Insomnia

---

## Next Steps

Once testing is complete:
1. Train the U-Net model on the Kaggle dataset
2. Build React frontend components
3. Add real-time visualization
4. Deploy to production

Happy testing! 🚀
