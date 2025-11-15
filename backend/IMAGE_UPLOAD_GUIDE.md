# Image Upload Guide - Files and Zip Support

## Overview

The `/auth/admin/import-images-file` endpoint now supports **both regular image files AND zip files**! You can:
- Upload single or multiple image files
- Upload zip files containing multiple images
- Upload a mix of both in the same request

This is perfect for bulk importing dental x-rays or other image datasets.

---

## Quick Start

### Endpoint

```
POST /auth/admin/import-images-file
```

**Same endpoint for everything!** No need to use different endpoints for files vs zips.

### Authentication

**Admin only** - Requires valid JWT token with admin privileges.

---

## Usage Examples

### 1. Upload Regular Image Files

**Postman:**
```
POST http://127.0.0.1:8000/auth/admin/import-images-file
Headers: Authorization: Bearer YOUR_TOKEN
Body (form-data):
  - files: [Select image1.jpg]
  - files: [Select image2.png]
  - files: [Select image3.jpg]
  - folder_name: dental-xrays (optional)
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/admin/import-images-file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -F "files=@image3.jpg" \
  -F "folder_name=dental-xrays"
```

---

### 2. Upload Zip File

**Postman:**
```
POST http://127.0.0.1:8000/auth/admin/import-images-file
Headers: Authorization: Bearer YOUR_TOKEN
Body (form-data):
  - files: [Select dental-images.zip]
  - folder_name: dental-xrays (optional)
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/admin/import-images-file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@dental-images.zip" \
  -F "folder_name=dental-xrays"
```

The endpoint **automatically detects** the zip file and extracts all images!

---

### 3. Upload Mix of Files and Zips

**You can upload regular files AND zips in the same request!**

```bash
curl -X POST "http://127.0.0.1:8000/auth/admin/import-images-file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@patient1.jpg" \
  -F "files=@dental-dataset.zip" \
  -F "files=@patient2.png" \
  -F "files=@more-images.zip" \
  -F "folder_name=dental-xrays"
```

---

### 4. Python Example

```python
import requests

url = "http://127.0.0.1:8000/auth/admin/import-images-file"
token = "YOUR_JWT_TOKEN"

headers = {
    "Authorization": f"Bearer {token}"
}

# Upload mix of regular files and zip
files = [
    ("files", open("image1.jpg", "rb")),
    ("files", open("images.zip", "rb")),
    ("files", open("image2.png", "rb")),
]

data = {
    "folder_name": "dental-xrays"  # Optional
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())

# Close files
for _, file_obj in files:
    file_obj.close()
```

---

## Supported Formats

### Image Files
- `.jpg` / `.jpeg`
- `.png`
- `.webp`

### Archive Files
- `.zip` (automatically extracted)

**File size limit:** 10MB per image (inside or outside zip)

---

## Response Format

### Success Response

```json
{
  "uploaded": 15,
  "failed": 1,
  "skipped": 2,
  "folder": "dental-xrays",
  "results": [
    {
      "id": 1,
      "filename": "image1.jpg",
      "image_url": "https://captcha-dental-images.s3.amazonaws.com/...",
      "source": "direct"
    },
    {
      "id": 2,
      "filename": "image2.jpg",
      "image_url": "https://captcha-dental-images.s3.amazonaws.com/...",
      "source": "zip:dental-images.zip"
    }
  ],
  "failures": [
    {
      "filename": "corrupted.jpg",
      "error": "Failed to upload to S3"
    }
  ],
  "skipped_files": [
    {
      "filename": "readme.txt",
      "reason": "Not an image file (extension: .txt)"
    },
    {
      "filename": "duplicate.jpg",
      "reason": "Image already exists in database"
    }
  ]
}
```

### Response Fields

- **`uploaded`** - Number of images successfully uploaded
- **`failed`** - Number of files that failed to upload
- **`skipped`** - Number of files that were skipped
- **`results`** - Array of successfully uploaded images
  - **`source`** - `"direct"` for regular files, `"zip:filename.zip"` for images from zip
- **`failures`** - Array of failed uploads with error messages
- **`skipped_files`** - Array of skipped files with reasons

---

## How Zip Files Work

### Automatic Detection

The endpoint automatically detects zip files by:
1. File extension (`.zip`)
2. Content type (`application/zip`)

No special handling needed - just upload like any other file!

### Filename Handling

Images are extracted from the zip using their **base filename only** (no folder paths):

**Zip structure:**
```
dental-images.zip
├── image1.jpg
├── image2.png
└── subfolder/
    └── image3.jpg
```

**Resulting filenames:**
- `image1.jpg`
- `image2.png`
- `image3.jpg` (folder path removed)

**Note:** If you have duplicate filenames in different folders (e.g., `folder1/tooth.jpg` and `folder2/tooth.jpg`), only the first one will be uploaded. The second will be skipped as a duplicate.

### Smart Filtering

The endpoint automatically skips:
- ✅ Directories (empty folders)
- ✅ macOS metadata (`__MACOSX/`, `.DS_Store`)
- ✅ Non-image files (`.txt`, `.pdf`, etc.)
- ✅ Duplicate images (already in database)
- ✅ Files larger than 10MB

All skipped files are reported in `skipped_files` array.

---

## Use Cases

### 1. Bulk Import from Kaggle

```bash
# Download Kaggle dataset (already a zip file)
kaggle datasets download -d username/dental-xrays

# Upload directly - no need to extract!
curl -X POST "http://127.0.0.1:8000/auth/admin/import-images-file" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@dental-xrays.zip"
```

### 2. Mixed Upload (Some Files, Some Zips)

```bash
# Upload specific images + bulk zip
curl -X POST "http://127.0.0.1:8000/auth/admin/import-images-file" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@urgent-case.jpg" \
  -F "files=@dental-archive.zip" \
  -F "files=@another-case.png"
```

### 3. Bulk Import with Unique Names

**Zip contents:**
```
dental-archive.zip
├── tooth-001.jpg
├── tooth-002.jpg
├── xray-a.png
└── xray-b.png
```

**Important:** Make sure all image files in your zip have unique names. If you have folders with duplicate filenames, rename them first!

---

## Comparison: Before vs After

| Scenario | Before | After |
|----------|--------|-------|
| **Upload 1 image** | `/import-images-file` | `/import-images-file` ✅ |
| **Upload 10 images** | `/import-images-file` | `/import-images-file` ✅ |
| **Upload zip** | `/import-images-zip` ❌ Different endpoint | `/import-images-file` ✅ Same endpoint |
| **Mix files + zip** | ❌ Not possible | `/import-images-file` ✅ Works! |

**One endpoint does it all!** 🎉

---

## Error Responses

### Invalid File Type (Non-image, Non-zip)

```json
{
  "uploaded": 0,
  "failed": 1,
  "failures": [
    {
      "filename": "document.pdf",
      "error": "Invalid file type: application/pdf. Allowed: JPEG, PNG, WEBP, or ZIP"
    }
  ]
}
```

### Invalid Zip File

```json
{
  "uploaded": 0,
  "failed": 1,
  "failures": [
    {
      "filename": "corrupted.zip",
      "error": "Invalid zip file"
    }
  ]
}
```

### Not Admin

```json
{
  "detail": "Only administrators can upload images"
}
```

---

## Configuration

### Change Max File Size

In [auth.py](api/routes/auth.py) line 714:

```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Change to 20MB:
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
```

### Add More Image Formats

In [auth.py](api/routes/auth.py):

```python
# Line 712 - Regular file uploads
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"}

# Line 713 - Zip file extraction
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Line 770 - Content type mapping for zip files
content_type_map = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.webp': 'image/webp',
    '.gif': 'image/gif'
}
```

---

## Troubleshooting

### Zip file not detected

**Issue:** Zip file uploaded but treated as regular file (fails validation)

**Solution:** Ensure file has `.zip` extension

```bash
# Correct
zip images.zip *.jpg

# Incorrect (creates .tar.gz, not .zip)
tar -czf images.tar.gz *.jpg
```

### All images skipped

**Issue:** All files in `skipped_files` array

**Check:**
1. Are they image files? (`.jpg`, `.png`, `.webp`)
2. Do they already exist in database?
3. Are they in `__MACOSX` or hidden folders?

**View skip reasons:**
```json
{
  "skipped_files": [
    {"filename": "readme.txt", "reason": "Not an image file"},
    {"filename": "image.jpg", "reason": "Image already exists in database"}
  ]
}
```

### Some images failed from zip

**Issue:** Some images in `failures` array

**Common reasons:**
- File too large (>10MB)
- Corrupted image inside zip
- S3 upload failed (check AWS credentials)

**View specific errors:**
```json
{
  "failures": [
    {
      "filename": "images.zip:large-image.jpg",
      "error": "File too large: 12000000 bytes. Max: 10485760 bytes"
    }
  ]
}
```

---

## Testing

### Test 1: Upload Regular Images

```bash
# Create test images
echo "test" > image1.jpg
echo "test" > image2.png

# Upload
curl -X POST "http://127.0.0.1:8000/auth/admin/import-images-file" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png"
```

### Test 2: Upload Zip

```bash
# Create zip with images
zip test-images.zip *.jpg

# Upload
curl -X POST "http://127.0.0.1:8000/auth/admin/import-images-file" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@test-images.zip"
```

### Test 3: Mixed Upload

```bash
# Upload both
curl -X POST "http://127.0.0.1:8000/auth/admin/import-images-file" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@single-image.jpg" \
  -F "files=@bulk-images.zip"
```

---

## Implementation Details

### File Type Detection

```python
# Check if file is a zip
is_zip = file.filename.endswith('.zip') or file.content_type == 'application/zip'

if is_zip:
    # Extract and upload all images from zip
    ...
else:
    # Upload regular image file
    ...
```

### Duplicate Prevention

The endpoint checks if an image with the same filename already exists:

```python
existing = db.query(Image).filter(Image.filename == clean_filename).first()
if existing:
    skipped.append({"filename": file_path, "reason": "Image already exists"})
    continue
```

### Source Tracking

Results include a `source` field showing where the image came from:
- `"source": "direct"` - Regular file upload
- `"source": "zip:filename.zip"` - Extracted from zip file

---

## Summary

✅ **Unified Endpoint:** One endpoint handles everything

✅ **Automatic Detection:** Detects and extracts zip files automatically

✅ **Mixed Uploads:** Upload files and zips together

✅ **Smart Processing:**
- Preserves folder structure in filenames
- Skips duplicates and non-images
- Detailed error reporting

✅ **Same Security:** Admin-only, file validation, private S3 bucket

✅ **Easy to Use:** No special configuration needed

Perfect for any image import scenario! 🦷
