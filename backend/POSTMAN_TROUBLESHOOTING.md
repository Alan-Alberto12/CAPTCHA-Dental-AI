# Postman Troubleshooting: "Could Not Get Response"

## ✅ Backend is Running

The backend is confirmed working. The issue is likely with your Postman setup.

---

## Step-by-Step Fix

### 1. Login First (Get Your Token)

**Create a login request:**

**Method:** `POST`

**URL:** `http://127.0.0.1:8000/auth/login`

**Headers:**
- Key: `Content-Type`
- Value: `application/x-www-form-urlencoded`

**Body:**
- Select **`x-www-form-urlencoded`**
- Add these keys:
  - Key: `username`, Value: `admin@captcha.local`
  - Key: `password`, Value: `admin123`

**Click Send**

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Copy the entire `access_token` value!**

---

### 2. Upload Image File

**Create a new request:**

**Method:** `POST`

**URL:** `http://127.0.0.1:8000/auth/admin/import-images-file`

**Headers Tab:**
1. Click "Headers" tab
2. Add header:
   - Key: `Authorization`
   - Value: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (paste your token after "Bearer ")

**Body Tab:**
1. Click "Body" tab
2. Select **`form-data`** radio button
3. In the table:
   - In the KEY column, type: `files`
   - Click the dropdown that appears next to `files` (it says "Text" by default)
   - **Change it to "File"**
   - Now a "Select Files" button appears in the VALUE column
   - Click "Select Files" and choose an image

**Click Send**

---

## Common Issues & Fixes

### Issue 1: "Could not get response"

**Causes:**
- Wrong URL (check it's exactly `http://127.0.0.1:8000/auth/admin/import-images-file`)
- Backend not running
- Network/firewall blocking localhost

**Fix:**
```bash
# Check backend is running:
docker ps | grep backend

# Should show:
# captcha-dental-backend ... Up ... 0.0.0.0:8000->8000/tcp
```

---

### Issue 2: "401 Unauthorized"

**Cause:** Missing or wrong token

**Fix:**
1. Make sure you have `Authorization` header
2. Value must be: `Bearer YOUR_TOKEN` (note the space after "Bearer")
3. Token might be expired (they last 30 minutes) - login again

---

### Issue 3: "403 Forbidden"

**Cause:** Not logged in as admin

**Fix:**
- Use admin credentials: `admin@captcha.local` / `admin123`
- Check your user has `is_admin: true`

---

### Issue 4: "422 Unprocessable Entity"

**Cause:** Body format is wrong

**Fix:**
1. Body tab → Select **`form-data`** (not raw, not binary)
2. Key must be exactly: `files` (plural)
3. Type must be: **File** (not Text)
4. Make sure you selected an image file

---

### Issue 5: Request Never Completes / Hangs

**Cause:** Large file or network issue

**Fix:**
1. Try a smaller image (< 1MB for testing)
2. Increase Postman timeout: Settings → General → Request timeout

---

## Verify Backend is Working

Test with this curl command in your terminal:

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@captcha.local&password=admin123"

# Copy the access_token from response

# 2. Test endpoint (replace YOUR_TOKEN)
curl -X POST http://127.0.0.1:8000/auth/admin/import-images-file \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@/path/to/your/image.jpg"
```

If curl works but Postman doesn't, the issue is definitely in your Postman setup.

---

## Postman Setup Checklist

Before clicking Send, verify:

- [ ] URL is `http://127.0.0.1:8000/auth/admin/import-images-file`
- [ ] Method is `POST`
- [ ] Headers tab has `Authorization: Bearer YOUR_TOKEN`
- [ ] Body tab has `form-data` selected
- [ ] Key is `files` (plural, lowercase)
- [ ] Type dropdown next to `files` shows "File" (not "Text")
- [ ] You clicked "Select Files" and chose an image
- [ ] Image is < 10MB
- [ ] Image is JPEG, PNG, or WEBP format

---

## Screenshots of Correct Postman Setup

### Headers Tab Should Look Like:
```
┌──────────────────┬────────────────────────────────────┐
│ KEY              │ VALUE                              │
├──────────────────┼────────────────────────────────────┤
│ Authorization    │ Bearer eyJhbGciOiJIUzI1NiIsInR... │
└──────────────────┴────────────────────────────────────┘
```

### Body Tab Should Look Like:
```
Select: ( ) none  ( ) form-data  (•) x-www-form  ( ) raw  ( ) binary  ( ) GraphQL

┌───────────┬──────┬─────────────────────┐
│ KEY       │ TYPE │ VALUE               │
├───────────┼──────┼─────────────────────┤
│ files     │ File │ [Select Files]  (1) │
└───────────┴──────┴─────────────────────┘
                ↑
           Must say "File"
```

---

## Still Not Working?

### Check Postman Console

1. Open Postman Console: View → Show Postman Console
2. Send your request
3. Look for errors in the console
4. Common errors:
   - Network error → Check Docker is running
   - CORS error → Should not happen with localhost
   - SSL error → Make sure URL is `http://` not `https://`

### Try Postman Collection

Import this collection:

```json
{
  "info": {
    "name": "CAPTCHA Dental AI",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/x-www-form-urlencoded"
          }
        ],
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            {"key": "username", "value": "admin@captcha.local"},
            {"key": "password", "value": "admin123"}
          ]
        },
        "url": "http://127.0.0.1:8000/auth/login"
      }
    },
    {
      "name": "Upload Images",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer YOUR_TOKEN_HERE"
          }
        ],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "files",
              "type": "file",
              "src": []
            }
          ]
        },
        "url": "http://127.0.0.1:8000/auth/admin/import-images-file?folder_name=test"
      }
    }
  ]
}
```

Copy this, then in Postman: Import → Raw text → Paste → Import

---

## Alternative: Use the URL Endpoint Instead

If file upload keeps failing, use the URL import endpoint:

**Method:** `POST`

**URL:** `http://127.0.0.1:8000/auth/admin/import-images-url`

**Headers:**
- `Authorization: Bearer YOUR_TOKEN`
- `Content-Type: application/json`

**Body:** (Select `raw` → `JSON`)
```json
{
  "images": [
    {
      "filename": "test.jpg",
      "image_url": "https://captcha-dental-images.s3.us-east-2.amazonaws.com/images/test.jpg"
    }
  ]
}
```

This is easier for testing and doesn't require file uploads!
