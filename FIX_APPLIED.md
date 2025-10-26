# Bug Fix Applied - SQLAlchemy Reserved Column Name

## Issue
The server was failing to start with the error:
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

## Root Cause
SQLAlchemy reserves the name `metadata` for its internal use in the Declarative Base class. We used `metadata = Column(JSON)` in several models.

## Fix Applied
Renamed all `metadata` columns to `extra_metadata` in:

1. ✅ [models/dataset.py](backend/models/dataset.py:20) - Line 20
2. ✅ [models/image.py](backend/models/image.py:57) - Line 57
3. ✅ [models/annotation.py](backend/models/annotation.py:30) - Line 30
4. ✅ [models/prediction.py](backend/models/prediction.py:34) - Line 34 (SegmentationModel)
5. ✅ [models/prediction.py](backend/models/prediction.py:71) - Line 71 (Prediction)

## Next Step - Install Dependencies

Before the server will work, you need to install the new dependencies:

```bash
cd backend
pip install -r requirements.txt
```

This will install all the ML libraries (PyTorch, OpenCV, kagglehub, etc.)

## Then Start Server

```bash
uvicorn main:app --reload
```

## Verification

After installing dependencies, verify with:
```bash
python scripts/test_integration.py
```

All 7 tests should pass! ✅
