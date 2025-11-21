# S3 Image Access Fix - Access Denied Error

## Problem

Images uploaded to S3 were showing "Access Denied" error when the frontend tried to display them. This is because:

1. ✅ Your S3 bucket is **private** (good for security!)
2. ❌ The frontend was trying to access images directly using permanent S3 URLs
3. ❌ Private buckets block direct public access

**Error you saw:**
```xml
<Error>
  <Code>AccessDenied</Code>
  <Message>Access Denied</Message>
</Error>
```

---

## Solution Applied: Presigned URLs ✅

The backend now **automatically generates temporary presigned URLs** for all images when they're sent to the frontend.

### What are Presigned URLs?

- **Temporary, secure URLs** that grant time-limited access to private S3 objects
- **Valid for 1 hour** (3600 seconds)
- **Automatically generated** by the backend when serving session data
- **No frontend changes needed** - it works transparently

### How it works:

```
Frontend requests session → Backend generates presigned URLs → Frontend displays images ✅
```

---

## What Was Changed

### Modified Files:

1. **[backend/api/routes/auth.py](api/routes/auth.py)**
   - `/sessions/current` endpoint (line 339)
   - `/sessions/start` endpoint (line 409)
   - `/sessions/start` return (line 503)

### Changes Made:

**Before:**
```python
"image_url": image.image_url  # Direct S3 URL (blocked)
```

**After:**
```python
# Generate presigned URL for private S3 bucket access (valid for 1 hour)
presigned_url = s3_service.generate_presigned_url(image.image_url, expiration=3600)
"image_url": presigned_url if presigned_url else image.image_url
```

---

## Testing

### 1. Upload an Image

```bash
POST /auth/admin/import-images-file
```

Response shows permanent S3 URL:
```json
{
  "image_url": "https://captcha-dental-images.s3.us-east-2.amazonaws.com/images/tooth_abc123.jpg"
}
```

### 2. Start/Get Session

```bash
GET /auth/sessions/current
```

Response shows **presigned URL** (with AWS signature):
```json
{
  "images": [
    {
      "image_url": "https://captcha-dental-images.s3.us-east-2.amazonaws.com/images/tooth_abc123.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...&X-Amz-Expires=3600&X-Amz-Signature=..."
    }
  ]
}
```

### 3. Frontend Displays Image

The frontend can now access the image using the presigned URL ✅

---

## URL Comparison

### Permanent S3 URL (stored in database):
```
https://captcha-dental-images.s3.us-east-2.amazonaws.com/images/tooth.jpg
```
- ❌ Blocked by private bucket
- ✅ Stored in database
- ✅ Doesn't expire

### Presigned URL (sent to frontend):
```
https://captcha-dental-images.s3.us-east-2.amazonaws.com/images/tooth.jpg?
  X-Amz-Algorithm=AWS4-HMAC-SHA256&
  X-Amz-Credential=AKIAQ563XODKKKM5SRXV/20251115/us-east-2/s3/aws4_request&
  X-Amz-Date=20251115T160000Z&
  X-Amz-Expires=3600&
  X-Amz-SignedHeaders=host&
  X-Amz-Signature=abcdef123456...
```
- ✅ Grants temporary access
- ✅ Valid for 1 hour
- ✅ Works with private bucket
- ❌ Expires after 1 hour

---

## Security Benefits

✅ **Bucket remains private** - No public access
✅ **Time-limited access** - URLs expire after 1 hour
✅ **AWS signature verification** - Can't be forged
✅ **No CORS issues** - Direct S3 access
✅ **Audit trail** - AWS logs all access

---

## Important Notes

### URL Expiration

Presigned URLs are valid for **1 hour (3600 seconds)**. After that:
- The URL becomes invalid
- User needs to refresh/get a new session
- Backend generates a new presigned URL

### Why 1 hour?

- Long enough for normal gameplay sessions
- Short enough to maintain security
- Can be adjusted in the code: `expiration=3600`

### Database Storage

- **Database stores:** Permanent S3 URL
- **API returns:** Temporary presigned URL
- This is intentional and correct!

---

## Alternative Solutions (Not Used)

### Option 1: Make Bucket Public ❌
```python
# Not recommended - security risk
s3_client.put_object(ACL='public-read', ...)
```
**Why not:**
- Anyone can access all images
- Can't revoke access
- Security vulnerability

### Option 2: Image Proxy Endpoint ❌
```python
@router.get("/images/{image_id}")
def get_image(image_id):
    # Download from S3 and stream to client
```
**Why not:**
- More server load
- Slower performance
- More complex

### Option 3: Presigned URLs ✅ (CHOSEN)
**Why yes:**
- Secure
- Fast (direct S3 access)
- Simple implementation
- Industry standard

---

## Troubleshooting

### Images still not showing?

1. **Check AWS credentials in `.env`:**
   ```
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   AWS_REGION=us-east-2
   AWS_S3_BUCKET=captcha-dental-images
   ```

2. **Check URL in frontend:**
   - Should have `X-Amz-Signature` parameter
   - Should have `X-Amz-Expires=3600`

3. **Check AWS permissions:**
   Your IAM user needs `s3:GetObject` permission

4. **Restart backend:**
   ```bash
   docker compose restart backend
   ```

### "SignatureDoesNotMatch" error?

- Wrong AWS credentials
- Check `.env` file
- Regenerate AWS access keys

### Images work but expire quickly?

- Presigned URLs are designed to expire (1 hour)
- User needs to refresh session to get new URLs
- This is normal and secure behavior

---

## Summary

✅ **Problem fixed:** Images now display in frontend
✅ **Security maintained:** Bucket remains private
✅ **No frontend changes needed:** Backend handles everything
✅ **Industry best practice:** Using presigned URLs

Your images should now display correctly! 🎉
