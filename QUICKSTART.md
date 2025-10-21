# Quick Start Guide - Teeth Segmentation

Get up and running with teeth segmentation in 5 minutes!

## Prerequisites

- Python 3.8+
- PostgreSQL 15+
- Docker (optional, for database)
- Kaggle account

## Step 1: Install Dependencies (2 minutes)

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Configure Kaggle API (1 minute)

1. Go to https://www.kaggle.com/account
2. Click "Create New Token" in the API section
3. Download `kaggle.json`
4. Move it to the right location:

**macOS/Linux:**
```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

**Windows:**
```cmd
mkdir %USERPROFILE%\.kaggle
move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\kaggle.json
```

## Step 3: Start Database (1 minute)

**Option A: Using Docker (recommended)**
```bash
docker-compose up -d
```

**Option B: Using local PostgreSQL**
```bash
# Make sure PostgreSQL is running
# Update .env with your database credentials
```

## Step 4: Test the Integration (1 minute)

```bash
python scripts/test_integration.py
```

You should see all tests passing ✅

## Step 5: Start the Server

```bash
uvicorn main:app --reload
```

The API will be available at: http://localhost:8000

## Step 6: Download the Dataset (Optional)

```bash
python scripts/download_kaggle_dataset.py
```

This downloads 598 dental X-rays with 15,318 tooth annotations.

## Step 7: Try the API

### 7.1 Get an Access Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=YOUR_USERNAME&password=YOUR_PASSWORD"
```

Save the `access_token` from the response.

### 7.2 Upload an Image

```bash
curl -X POST "http://localhost:8000/images/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/dental_xray.png" \
  -F "image_type=panoramic"
```

Note the `image.id` from the response.

### 7.3 Run Segmentation

```bash
curl -X POST "http://localhost:8000/predictions/predict" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 1,
    "confidence_threshold": 0.5
  }'
```

### 7.4 Visualize Results

Open in browser:
```
http://localhost:8000/predictions/image/1/visualize
```

Or download:
```bash
curl "http://localhost:8000/predictions/image/1/visualize" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o result.png
```

## What's Next?

### Train a Model

The default U-Net is untrained. To get real predictions:

1. **Download the dataset** (Step 6 above)
2. **Write a training script** using PyTorch
3. **Save the model** to `./models/`
4. **Register it** in the database
5. **Use it** for predictions

### Build the Frontend

Check out the React component example in [TEETH_SEGMENTATION_GUIDE.md](TEETH_SEGMENTATION_GUIDE.md#frontend-integration)

### Explore the API

Visit the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### "No module named 'torch'"
```bash
pip install -r requirements.txt
```

### "Failed to download dataset"
1. Check Kaggle API is configured: `cat ~/.kaggle/kaggle.json`
2. Accept dataset terms on Kaggle's website
3. Verify internet connection

### "Database connection failed"
1. Check PostgreSQL is running: `docker-compose ps`
2. Verify credentials in `.env`
3. Create database if needed

### "Model prediction failed"
The default model is untrained - you'll need to train it first or the predictions will be random.

## File Structure

```
CAPTCHA-Dental-AI/
├── backend/
│   ├── models/           # Database models ✅
│   │   ├── dataset.py
│   │   ├── image.py
│   │   ├── annotation.py
│   │   └── prediction.py
│   ├── services/         # Business logic ✅
│   │   ├── kaggle_service.py
│   │   ├── dicom_service.py
│   │   └── segmentation_service.py
│   ├── api/routes/       # API endpoints ✅
│   │   ├── dataset.py
│   │   ├── images.py
│   │   └── predictions.py
│   └── scripts/          # Utility scripts ✅
│       ├── download_kaggle_dataset.py
│       └── test_integration.py
├── TEETH_SEGMENTATION_GUIDE.md    # Full guide ✅
├── IMPLEMENTATION_SUMMARY.md      # What was built ✅
└── QUICKSTART.md                  # This file ✅
```

## Resources

- **Full Guide**: [TEETH_SEGMENTATION_GUIDE.md](TEETH_SEGMENTATION_GUIDE.md)
- **Implementation Details**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **API Docs**: http://localhost:8000/docs
- **Kaggle Dataset**: https://www.kaggle.com/datasets/humansintheloop/teeth-segmentation-on-dental-x-ray-images

## Need Help?

1. Check the full guide: [TEETH_SEGMENTATION_GUIDE.md](TEETH_SEGMENTATION_GUIDE.md)
2. Run the test script: `python scripts/test_integration.py`
3. Check API logs for errors
4. Verify all dependencies are installed

Happy segmenting! 🦷✨
