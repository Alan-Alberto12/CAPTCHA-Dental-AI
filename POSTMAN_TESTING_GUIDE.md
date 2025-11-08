# Postman Testing Guide - CAPTCHA Dental AI

## 🚀 Setup

**Base URL:** `http://localhost:8000`

All authenticated requests need a Bearer token in the Authorization header.

---

## 📋 Testing Workflow

### Step 1: Create Account

**Endpoint:** `POST /auth/signup`

**Body (JSON):**
```json
{
  "email": "alan@test.com",
  "username": "alan_alberto",
  "password": "password123",
  "first_name": "Alan",
  "last_name": "Alberto"
}
```

**Expected Response (201):**
```json
{
  "id": 1,
  "email": "alan@test.com",
  "username": "alan_alberto",
  "first_name": "Alan",
  "last_name": "Alberto",
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-11-08T..."
}
```

---

### Step 2: Check Email Confirmation

**Open MailHog:** http://localhost:8025

- You'll see a confirmation email
- Copy the token from the URL (after `?token=`)

---

### Step 3: Confirm Email

**Endpoint:** `POST /auth/confirm-email`

**Body (JSON):**
```json
{
  "token": "PASTE_TOKEN_HERE"
}
```

**Expected Response (200):**
```json
{
  "message": "Email successfully confirmed!"
}
```

---

### Step 4: Login

**Endpoint:** `POST /auth/login`

**Body (x-www-form-urlencoded):**
```
username: alan@test.com
password: password123
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**⚠️ IMPORTANT:** Copy this `access_token` - you'll need it for all authenticated requests!

---

### Step 5: Promote to Admin

**Endpoint:** `POST /auth/admin/promote`

**Authorization:** Bearer Token (paste the access_token)

**Body (JSON):**
```json
{
  "email": "alan@test.com"
}
```

**Expected Response (200):**
```json
{
  "id": 1,
  "email": "alan@test.com",
  "username": "alan_alberto",
  "is_admin": true,
  ...
}
```

---

### Step 6: Import Images (Admin Only)

**Endpoint:** `POST /auth/admin/import-images`

**Authorization:** Bearer Token

**Body (JSON):**
```json
{
  "images": [
    {
      "filename": "tooth14_a.jpg",
      "image_url": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95"
    },
    {
      "filename": "tooth12_b.jpg",
      "image_url": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5"
    },
    {
      "filename": "tooth14_c.jpg",
      "image_url": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95"
    },
    {
      "filename": "cavity_d.jpg",
      "image_url": "https://images.unsplash.com/photo-1629909615957-be38c3a5f770"
    },
    {
      "filename": "tooth16_e.jpg",
      "image_url": "https://images.unsplash.com/photo-1598531228433-d9f0b5e5c2c7"
    }
  ]
}
```

**Expected Response (201):**
```json
{
  "message": "Images imported successfully",
  "images_imported": 5
}
```

---

### Step 7: Import Questions (Admin Only)

**Endpoint:** `POST /auth/admin/import-questions`

**Authorization:** Bearer Token

**No Body Required**

**Expected Response (201):**
```json
{
  "message": "Questions imported successfully",
  "questions_imported": 5
}
```

---

### Step 8: Get Next Session

**Endpoint:** `GET /auth/sessions/next?num_images=4&num_questions=2`

**Authorization:** Bearer Token

**Query Parameters:**
- `num_images`: Number of images to show (default: 4)
- `num_questions`: Number of questions to ask (default: 5)

**Expected Response (200):**
```json
{
  "session_id": 1,
  "images": [
    {
      "id": 1,
      "filename": "tooth14_a.jpg",
      "image_url": "https://...",
      "order": 1
    },
    {
      "id": 2,
      "filename": "tooth12_b.jpg",
      "image_url": "https://...",
      "order": 2
    },
    {
      "id": 3,
      "filename": "tooth14_c.jpg",
      "image_url": "https://...",
      "order": 3
    },
    {
      "id": 4,
      "filename": "cavity_d.jpg",
      "image_url": "https://...",
      "order": 4
    }
  ],
  "questions": [
    {
      "id": 1,
      "question_text": "Select all images showing tooth #14",
      "question_type": "tooth_number",
      "order": 1
    },
    {
      "id": 2,
      "question_text": "Select all images with cavities",
      "question_type": "cavity_detection",
      "order": 2
    }
  ],
  "started_at": "2025-11-08T..."
}
```

**📝 Note:** Save the `session_id`, `image IDs`, and `question IDs` - you'll need them next!

---

### Step 9: Submit Annotation (Answer Question)

**Endpoint:** `POST /auth/annotations`

**Authorization:** Bearer Token

**Body (JSON):**
```json
{
  "session_id": 1,
  "question_id": 1,
  "selected_image_ids": [1, 3],
  "time_spent": 8.5
}
```

**Explanation:**
- `session_id`: From Step 8
- `question_id`: Question #1 (tooth #14)
- `selected_image_ids`: User selected images #1 and #3 (both have tooth #14)
- `time_spent`: User took 8.5 seconds

**Expected Response (201):**
```json
{
  "id": 1,
  "session_id": 1,
  "question_id": 1,
  "selected_image_ids": [1, 3],
  "is_correct": null,
  "time_spent": 8.5,
  "created_at": "2025-11-08T..."
}
```

---

### Step 10: Submit Another Annotation

**Endpoint:** `POST /auth/annotations`

**Authorization:** Bearer Token

**Body (JSON):**
```json
{
  "session_id": 1,
  "question_id": 2,
  "selected_image_ids": [4],
  "time_spent": 12.3
}
```

**Explanation:**
- Question #2: "Select cavities"
- User selected only image #4 (cavity image)

**Expected Response (201):**
```json
{
  "id": 2,
  "session_id": 1,
  "question_id": 2,
  "selected_image_ids": [4],
  "is_correct": null,
  "time_spent": 12.3,
  "created_at": "2025-11-08T..."
}
```

---

## 🔍 Validation Endpoints

### Get My Annotations

**Endpoint:** `GET /auth/annotations/me`

**Authorization:** Bearer Token

**Expected Response (200):**
```json
[
  {
    "id": 2,
    "session_id": 1,
    "question_id": 2,
    "selected_image_ids": [4],
    "is_correct": null,
    "time_spent": 12.3,
    "created_at": "2025-11-08T..."
  },
  {
    "id": 1,
    "session_id": 1,
    "question_id": 1,
    "selected_image_ids": [1, 3],
    "is_correct": null,
    "time_spent": 8.5,
    "created_at": "2025-11-08T..."
  }
]
```

---

### Get Current User Info

**Endpoint:** `GET /auth/me`

**Authorization:** Bearer Token

**Expected Response (200):**
```json
{
  "id": 1,
  "email": "alan@test.com",
  "username": "alan_alberto",
  "first_name": "Alan",
  "last_name": "Alberto",
  "is_active": true,
  "is_admin": true,
  "created_at": "2025-11-08T...",
  "stats": {
    "total_points": 0,
    "total_annotations": 2,
    "accuracy_rate": 0.0,
    "daily_streak": 0
  }
}
```

---

## ❌ Error Scenarios to Test

### 1. Submit annotation with wrong image IDs

**Body:**
```json
{
  "session_id": 1,
  "question_id": 1,
  "selected_image_ids": [99, 100],
  "time_spent": 5.0
}
```

**Expected Response (400):**
```json
{
  "detail": "Image 99 is not part of this session"
}
```

---

### 2. Submit annotation with wrong question ID

**Body:**
```json
{
  "session_id": 1,
  "question_id": 999,
  "selected_image_ids": [1, 2],
  "time_spent": 5.0
}
```

**Expected Response (400):**
```json
{
  "detail": "Question is not part of this session"
}
```

---

### 3. Try to access another user's session

Create a second user, login, and try to submit annotation for session #1.

**Expected Response (403):**
```json
{
  "detail": "This session doesn't belong to you"
}
```

---

## 📊 Database Verification (Optional)

If you want to see the actual database data:

```bash
docker exec -it captcha-dental-db psql -U captcha_user -d captcha_dental_db
```

Then run:

```sql
-- See all sessions
SELECT * FROM sessions;

-- See images in a session
SELECT si.session_id, si.image_order, i.filename
FROM session_images si
JOIN images i ON si.image_id = i.id
WHERE si.session_id = 1;

-- See user's selected images
SELECT ai.annotation_id, i.filename
FROM annotation_images ai
JOIN images i ON ai.image_id = i.id
WHERE ai.annotation_id = 1;
```

---

## 🎯 Complete Test Flow Summary

1. ✅ Signup → Confirm Email → Login
2. ✅ Promote to Admin
3. ✅ Import 5 images
4. ✅ Import 5 questions
5. ✅ Get session (4 images, 2 questions)
6. ✅ Answer question #1 (select images 1, 3)
7. ✅ Answer question #2 (select image 4)
8. ✅ View all annotations
9. ✅ Check user stats

**You're done! The system is working!** 🎉
