# Teeth Segmentation Integration Guide

This guide explains how to use the Kaggle teeth segmentation dataset and DICOM functionality in your CAPTCHA Dental AI system.

## Table of Contents
1. [Overview](#overview)
2. [Setup](#setup)
3. [Dataset Download](#dataset-download)
4. [DICOM Support](#dicom-support)
5. [API Usage](#api-usage)
6. [Model Training](#model-training)
7. [Frontend Integration](#frontend-integration)

---

## Overview

The integration includes:
- **Kaggle Dataset**: [Teeth Segmentation on Dental X-ray Images](https://www.kaggle.com/datasets/humansintheloop/teeth-segmentation-on-dental-x-ray-images)
  - 598 panoramic dental X-ray images
  - 15,318 manually annotated tooth polygons
  - Each tooth segmented with a different class
  - Annotations by 12 trainees in the Democratic Republic of Congo

- **DICOM Support**: Full support for medical imaging DICOM files
- **ML Pipeline**: End-to-end pipeline for training and inference
- **REST API**: Complete API for image upload, prediction, and visualization

---

## Setup

### 1. Install Dependencies

First, install the new dependencies:

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- **PyTorch**: Deep learning framework
- **OpenCV**: Image processing
- **pydicom**: DICOM file handling
- **kagglehub**: Kaggle dataset downloads
- **albumentations**: Image augmentation
- And more...

### 2. Configure Kaggle API

To download datasets from Kaggle, you need to configure your Kaggle API credentials:

1. Go to https://www.kaggle.com/account
2. Scroll to "API" section
3. Click "Create New Token"
4. This downloads `kaggle.json`
5. Place it in the correct location:

**On macOS/Linux:**
```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

**On Windows:**
```cmd
mkdir %USERPROFILE%\.kaggle
move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\kaggle.json
```

### 3. Update Database

The new database models will be created automatically when you start the server. Make sure PostgreSQL is running:

```bash
# If using Docker
docker-compose up -d

# Start the backend
cd backend
uvicorn main:app --reload
```

---

## Dataset Download

### Method 1: Using the Script (Recommended)

Run the provided script to download and process the dataset:

```bash
cd backend
python scripts/download_kaggle_dataset.py
```

This will:
1. Download the dataset from Kaggle (~200MB)
2. Process all images and annotations
3. Import into your database
4. Show statistics

### Method 2: Using the API

You can also use the API endpoints:

```bash
# Login first to get a token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=yourpassword"

# Download dataset
curl -X POST "http://localhost:8000/datasets/download" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "kaggle_path": "humansintheloop/teeth-segmentation-on-dental-x-ray-images",
    "name": "Teeth Segmentation Dataset"
  }'
```

### Method 3: Using Python Code

```python
import kagglehub

# Download latest version
path = kagglehub.dataset_download("humansintheloop/teeth-segmentation-on-dental-x-ray-images")

print("Path to dataset files:", path)
```

---

## DICOM Support

### Upload DICOM Files

The system automatically detects and processes DICOM files:

```bash
# Upload a DICOM file
curl -X POST "http://localhost:8000/images/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/dental_xray.dcm" \
  -F "image_type=dicom" \
  -F "convert_dicom=true"
```

### DICOM Features

The DICOM service provides:
- **Automatic detection** of DICOM files
- **Metadata extraction** (patient info, study details, etc.)
- **Automatic conversion** to PNG for visualization
- **Window/Level adjustment** for optimal viewing
- **Anonymization** support
- **Batch processing** capabilities

### Using DICOM Service in Code

```python
from services.dicom_service import DICOMService
from services.database import SessionLocal

db = SessionLocal()
dicom_service = DICOMService(db)

# Process a DICOM file
image, converted_path = dicom_service.process_dicom_upload(
    dicom_file_path="path/to/file.dcm",
    user_id=1,
    convert_to_png=True
)

print(f"DICOM metadata: {image.dicom_metadata}")
print(f"Converted image: {converted_path}")
```

---

## API Usage

### 1. Dataset Endpoints

```bash
# List datasets
GET /datasets/

# Get dataset statistics
GET /datasets/{dataset_id}/stats

# Process dataset
POST /datasets/{dataset_id}/process
```

### 2. Image Upload Endpoints

```bash
# Upload image (supports DICOM, PNG, JPG, TIFF)
POST /images/upload

# List images
GET /images/

# Get image
GET /images/{image_id}

# Download image
GET /images/{image_id}/download?dicom=true
```

### 3. Prediction Endpoints

```bash
# Run prediction
POST /predictions/predict
{
  "image_id": 1,
  "model_id": null,  # uses default
  "confidence_threshold": 0.5
}

# Get predictions for image
GET /predictions/image/{image_id}

# Visualize predictions
GET /predictions/image/{image_id}/visualize

# Verify prediction (human feedback)
POST /predictions/{prediction_id}/verify
{
  "is_correct": true
}
```

### 4. Model Endpoints

```bash
# List available models
GET /predictions/models/

# Get model details
GET /predictions/models/{model_id}
```

---

## Model Training

### Pre-trained Models

The system includes a basic U-Net architecture. For production use, you should:

1. **Train on the Kaggle dataset**
2. **Use a proven architecture** (U-Net, Mask R-CNN, DeepLabV3+)
3. **Fine-tune hyperparameters**

### Training Script Example

```python
from services.database import SessionLocal
from services.kaggle_service import KaggleDatasetService
from services.segmentation_service import SegmentationService, UNet
import torch

# Setup
db = SessionLocal()
kaggle_service = KaggleDatasetService(db)

# Get dataset
dataset = db.query(Dataset).filter(Dataset.id == 1).first()

# Load images and annotations
images = db.query(Image).filter(Image.dataset_id == dataset.id).all()
annotations = db.query(Annotation).all()

# Initialize model
model = UNet(in_channels=1, num_classes=32)

# Train model (simplified)
# ... your training loop here ...

# Save model
torch.save(model.state_dict(), "./models/unet_teeth_segmentation.pth")

# Register in database
seg_model = SegmentationModel(
    name="Teeth Segmentation U-Net",
    version="1.0",
    architecture="U-Net",
    model_path="./models/unet_teeth_segmentation.pth",
    num_classes=32,
    input_size=[512, 512],
    is_active=True,
    is_default=True,
)
db.add(seg_model)
db.commit()
```

### Recommended Architectures

1. **U-Net**: Good for medical imaging, included in the codebase
2. **Mask R-CNN**: For instance segmentation with bounding boxes
3. **DeepLabV3+**: State-of-the-art semantic segmentation
4. **SegFormer**: Transformer-based segmentation

---

## Frontend Integration

### Basic React Component Example

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function TeethSegmentation() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [imageId, setImageId] = useState(null);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('image_type', 'panoramic');

    try {
      const response = await axios.post(
        'http://localhost:8000/images/upload',
        formData,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setImageId(response.data.image.id);
      alert('Image uploaded successfully!');
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handlePredict = async () => {
    try {
      const response = await axios.post(
        'http://localhost:8000/predictions/predict',
        {
          image_id: imageId,
          confidence_threshold: 0.5
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      setPredictions(response.data);
      alert(`Found ${response.data.total_predictions} teeth!`);
    } catch (error) {
      console.error('Prediction failed:', error);
    }
  };

  return (
    <div>
      <h2>Teeth Segmentation</h2>

      <input
        type="file"
        accept=".dcm,.png,.jpg,.jpeg"
        onChange={(e) => setSelectedFile(e.target.files[0])}
      />

      <button onClick={handleUpload}>Upload Image</button>

      {imageId && (
        <button onClick={handlePredict}>Run Segmentation</button>
      )}

      {predictions && (
        <div>
          <h3>Results</h3>
          <p>Total teeth detected: {predictions.total_predictions}</p>
          <p>Inference time: {predictions.inference_time.toFixed(3)}s</p>

          <img
            src={`http://localhost:8000/predictions/image/${imageId}/visualize`}
            alt="Segmentation result"
          />
        </div>
      )}
    </div>
  );
}

export default TeethSegmentation;
```

---

## Database Schema

### New Tables Created

1. **datasets**: Kaggle dataset metadata
2. **images**: X-ray images (from dataset or user uploads)
3. **annotations**: Manual annotations from Kaggle dataset
4. **predictions**: AI predictions
5. **segmentation_models**: ML model metadata

### Relationships

```
datasets (1) --> (N) images
images (1) --> (N) annotations
images (1) --> (N) predictions
segmentation_models (1) --> (N) predictions
users (1) --> (N) images
users (1) --> (N) predictions
```

---

## Tooth Notation

The dataset uses FDI (Fédération Dentaire Internationale) notation:

- **Adult teeth**: Classes 1-32
- **Quadrants**:
  - Upper right: 11-18
  - Upper left: 21-28
  - Lower left: 31-38
  - Lower right: 41-48

---

## Performance Metrics

The system tracks:
- **IoU (Intersection over Union)**: Overlap between prediction and ground truth
- **Dice Coefficient**: Similarity measure
- **Accuracy**: Overall classification accuracy
- **Inference Time**: Speed of predictions

---

## Troubleshooting

### Kaggle Download Issues

If dataset download fails:
1. Check your Kaggle API token is configured
2. Verify you've accepted the dataset terms on Kaggle's website
3. Check your internet connection
4. Try downloading manually and place in `./data/` directory

### DICOM Processing Issues

If DICOM files aren't processing:
1. Verify the file is a valid DICOM (use a DICOM viewer)
2. Check file permissions
3. Ensure pydicom is installed correctly
4. Try converting manually with the DICOMService

### Model Prediction Issues

If predictions fail:
1. Verify the model exists in the database
2. Check model file path is correct
3. Ensure PyTorch is installed with correct version
4. Check image format and size

---

## Next Steps

1. **Download the dataset** using the script
2. **Train a model** on your data
3. **Test predictions** via the API
4. **Build the frontend** components
5. **Deploy to production**

For questions or issues, please refer to the main project README or create an issue on GitHub.

---

## License

This integration uses:
- Kaggle Dataset: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- PyTorch: BSD License
- pydicom: MIT License

Please ensure you comply with all relevant licenses when using this system.
