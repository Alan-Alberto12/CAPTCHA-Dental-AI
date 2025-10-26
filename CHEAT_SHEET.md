# Testing Cheat Sheet - Quick Reference

## 🚀 One-Line Tests

### Test Everything (Recommended)
```bash
cd backend && python scripts/quick_test.py
```

### Test Integration Only
```bash
cd backend && python scripts/test_integration.py
```

### Download Kaggle Dataset
```bash
cd backend && python scripts/download_kaggle_dataset.py
```

### Start Server
```bash
cd backend && uvicorn main:app --reload
```

### Open Interactive API Docs
```bash
# macOS
open http://localhost:8000/docs

# Linux
xdg-open http://localhost:8000/docs

# Or just visit in browser:
http://localhost:8000/docs
```

---

## 🔧 Setup Commands

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Kaggle
```bash
# Download from https://www.kaggle.com/account
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 3. Start Database
```bash
docker-compose up -d
```

### 4. Create Tables
```bash
cd backend
python scripts/create_tables.py
```

---

## 🧪 Quick API Tests (cURL)

### Get Token
```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -d "username=testuser&password=testpass123"

# Save token
export TOKEN="paste_your_token_here"
```

### Upload Image
```bash
curl -X POST "http://localhost:8000/images/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@image.png" \
  -F "image_type=panoramic"
```

### Run Prediction
```bash
curl -X POST "http://localhost:8000/predictions/predict" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_id": 1, "confidence_threshold": 0.5}'
```

### Download Visualization
```bash
curl "http://localhost:8000/predictions/image/1/visualize" \
  -H "Authorization: Bearer $TOKEN" \
  -o result.png && open result.png
```

---

## 🐍 Quick Python Tests

### Test Kaggle Download
```python
import kagglehub
path = kagglehub.dataset_download("humansintheloop/teeth-segmentation-on-dental-x-ray-images")
print("Dataset:", path)
```

### Test DICOM Service
```python
from services.database import SessionLocal
from services.dicom_service import DICOMService

db = SessionLocal()
service = DICOMService(db)
print(f"Upload dir: {service.upload_dir}")
```

### Test Segmentation Service
```python
from services.database import SessionLocal
from services.segmentation_service import SegmentationService

db = SessionLocal()
service = SegmentationService(db)
print(f"Device: {service.device}")
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide |
| [TESTING_WITHOUT_FRONTEND.md](TESTING_WITHOUT_FRONTEND.md) | Complete testing guide |
| [TEETH_SEGMENTATION_GUIDE.md](TEETH_SEGMENTATION_GUIDE.md) | Full documentation |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | What was built |

---

## 🔗 Useful URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000 | API root |
| http://localhost:8000/docs | Swagger UI (Interactive API) ⭐ |
| http://localhost:8000/redoc | ReDoc (Alternative docs) |
| http://localhost:8000/health | Health check |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: torch` | `pip install -r requirements.txt` |
| `Kaggle credentials not found` | Configure `~/.kaggle/kaggle.json` |
| `Database connection error` | `docker-compose up -d` |
| `Server not running` | `uvicorn main:app --reload` |
| `Predictions are random` | Model needs training (expected) |

---

## 📊 Expected Results

### Test Suite (7/7 tests)
```
✅ Database Models
✅ Service Imports
✅ Kaggle Service
✅ DICOM Service
✅ Segmentation Service
✅ API Routes
✅ Dependencies
```

### Dataset Download
```
✅ 598 images downloaded
✅ 15,318 annotations processed
✅ ~200MB storage used
```

### Prediction
```
✅ Image uploaded
✅ Prediction completed
✅ Teeth detected (if model trained)
✅ Visualization generated
```

---

## 🎯 Testing Methods (Choose One)

1. **Quick Test Script** (Easiest)
   ```bash
   python scripts/quick_test.py
   ```

2. **Swagger UI** (Most Visual)
   - Open http://localhost:8000/docs
   - Click endpoints to test

3. **cURL Commands** (CLI)
   - See [TESTING_WITHOUT_FRONTEND.md](TESTING_WITHOUT_FRONTEND.md)

4. **Python Scripts** (Automated)
   - Create custom test scripts

5. **Postman/Insomnia** (GUI)
   - Import collection from docs

---

## 🔥 Most Common Commands

```bash
# Full workflow
cd backend
pip install -r requirements.txt
docker-compose up -d
python scripts/test_integration.py
python scripts/download_kaggle_dataset.py
uvicorn main:app --reload

# In another terminal
python scripts/quick_test.py

# Or open browser
open http://localhost:8000/docs
```

---

## 💡 Pro Tips

1. **Use Swagger UI** - It's the easiest way to test APIs interactively
2. **Save your token** - Export it as environment variable
3. **Check logs** - Server shows all requests in real-time
4. **Use quick_test.py** - Tests everything in one command
5. **Train the model** - Default model is untrained (predictions are random)

---

## 📚 More Help

- **Full Guide**: [TEETH_SEGMENTATION_GUIDE.md](TEETH_SEGMENTATION_GUIDE.md)
- **Testing Guide**: [TESTING_WITHOUT_FRONTEND.md](TESTING_WITHOUT_FRONTEND.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **API Docs**: http://localhost:8000/docs

---

**TL;DR: Run this one command to test everything:**
```bash
cd backend && python scripts/quick_test.py
```
