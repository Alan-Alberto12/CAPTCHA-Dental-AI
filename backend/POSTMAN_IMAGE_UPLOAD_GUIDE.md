# Postman Image Upload Guide

## Two Ways to Import Images

### 1. **`import-images-url`** - From URLs (JSON)
Use when you already have images hosted somewhere (S3, etc.)

### 2. **`import-images-file`** - Upload Files (Form Data)
Use when you have image files on your computer

---

## Option 1: Import from URLs

**Endpoint:** `POST http://127.0.0.1:8000/auth/admin/import-images-url`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json
```

**Body Type:** `raw` → `JSON`

**Body:**
```json
{
  "images": [
    {
      "filename": "tooth1.jpg",
      "image_url": "https://captcha-dental-images.s3.us-east-2.amazonaws.com/images/tooth1.jpg"
    },
    {
      "filename": "tooth2.jpg",
      "image_url": "https://captcha-dental-images.s3.us-east-2.amazonaws.com/images/tooth2.jpg"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Images imported successfully",
  "images_imported": 2
}
```

---

## Option 2: Upload Image Files

**Endpoint:** `POST http://127.0.0.1:8000/auth/admin/import-images-file?folder_name=dental-xrays`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN_HERE
```

**Body Type:** `form-data`

**Body Setup:**

### For Single File:
```
┌─────────┬──────┬──────────────────────┐
│ KEY     │ TYPE │ VALUE                │
├─────────┼──────┼──────────────────────┤
│ files   │ File │ [Select Files]       │
└─────────┴──────┴──────────────────────┘
```

### For Multiple Files:
```
┌─────────┬──────┬──────────────────────┐
│ KEY     │ TYPE │ VALUE                │
├─────────┼──────┼──────────────────────┤
│ files   │ File │ image1.jpg           │
│ files   │ File │ image2.jpg           │
│ files   │ File │ image3.jpg           │
└─────────┴──────┴──────────────────────┘
```

**Note:** Same key name `files` for all uploads!

**Response:**
```json
{
  "uploaded": 3,
  "failed": 0,
  "folder": "dental-xrays",
  "results": [
    {
      "id": 1,
      "filename": "image1.jpg",
      "image_url": "https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/image1_a1b2c3d4.jpg"
    },
    {
      "id": 2,
      "filename": "image2.jpg",
      "image_url": "https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/image2_e5f6g7h8.jpg"
    },
    {
      "id": 3,
      "filename": "image3.jpg",
      "image_url": "https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/image3_i9j0k1l2.jpg"
    }
  ],
  "failures": []
}
```

---

## Step-by-Step in Postman

### Step 1: Login to Get Token

**Method:** `POST`

**URL:** `http://127.0.0.1:8000/auth/login`

**Body (raw JSON):**
```json
{
  "email": "admin@captcha.local",
  "password": "admin123"
}
```

**Copy the `access_token` from response**

---

### Step 2a: Upload Files (Recommended)

**Method:** `POST`

**URL:** `http://127.0.0.1:8000/auth/admin/import-images-file?folder_name=dental-xrays`

**Headers Tab:**
- Key: `Authorization`
- Value: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (paste your token)

**Body Tab:**
1. Select **form-data**
2. Click on "KEY" dropdown → change from "Text" to **"File"**
3. Enter key: `files`
4. Click "Select Files" → choose your image(s)
5. To add more images:
   - Add another row
   - Key: `files` (same name!)
   - Type: File
   - Select another image

**Click Send**

---

### Step 2b: Import from URLs (Alternative)

**Method:** `POST`

**URL:** `http://127.0.0.1:8000/auth/admin/import-images-url`

**Headers Tab:**
- Key: `Authorization`
- Value: `Bearer YOUR_TOKEN`
- Key: `Content-Type`
- Value: `application/json`

**Body Tab:**
1. Select **raw**
2. Select **JSON** from dropdown
3. Paste JSON with image URLs

**Click Send**

---

## Organizing with Folders

Add `?folder_name=YOUR_FOLDER` to the URL:

- **Cavities:** `?folder_name=cavities`
- **X-rays:** `?folder_name=xrays`
- **Healthy:** `?folder_name=healthy`
- **Implants:** `?folder_name=implants`

Example:
```
http://127.0.0.1:8000/auth/admin/import-images-file?folder_name=dental-cavities
```

Files will be stored in S3 as:
```
dental-cavities/image1_abc123.jpg
dental-cavities/image2_def456.jpg
```

---

## File Requirements

**Accepted formats:**
- JPEG / JPG
- PNG
- WEBP

**Max file size:** 10 MB per file

**No limit** on number of files (can upload all at once)

---

## Comparison

| Feature | import-images-url | import-images-file |
|---------|-------------------|---------------------|
| **Body Type** | JSON | form-data |
| **Use Case** | Images already in S3 | Upload from computer |
| **Upload to S3** | ❌ No | ✅ Yes |
| **Single/Bulk** | ✅ Both | ✅ Both |
| **Easier for** | Migration/Scripts | Manual uploads |

---

## Troubleshooting

### "401 Unauthorized"
- Token expired (30 min lifetime)
- Login again to get fresh token

### "403 Forbidden"
- Not logged in as admin
- Check user has `is_admin: true`

### "Invalid file type"
- Only JPEG, PNG, WEBP allowed
- Check file extension matches content

### "File too large"
- Max 10MB per file
- Compress/resize image

### "AWS credentials not configured"
- Add to `.env`:
  ```
  AWS_ACCESS_KEY_ID=your-key
  AWS_SECRET_ACCESS_KEY=your-secret
  AWS_REGION=us-east-2
  AWS_S3_BUCKET=captcha-dental-images
  ```

### "Failed to upload to S3"
- Check AWS credentials
- Check S3 bucket exists
- Check bucket permissions

---

## Quick Test

**Minimal test with one file:**

1. Login: `POST /auth/login`
2. Copy token
3. Upload: `POST /auth/admin/import-images-file`
   - Header: `Authorization: Bearer <token>`
   - Body: form-data, key=`files`, type=File, select image
4. Send!

✅ If you get a response with `"uploaded": 1`, it worked!
