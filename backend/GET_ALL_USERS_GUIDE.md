# Get All Users Endpoint

## Endpoint Details

**URL:** `GET /auth/admin/users`

**Authentication:** Admin only (requires valid admin token)

**Response:** List of all users in the system, ordered by most recent first

---

## Using in Postman

### Step 1: Login as Admin

**Method:** `POST`

**URL:** `http://127.0.0.1:8000/auth/login`

**Body:** (x-www-form-urlencoded)
```
username: admin@captcha.local
password: admin123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Copy the `access_token`!**

---

### Step 2: Get All Users

**Method:** `GET`

**URL:** `http://127.0.0.1:8000/auth/admin/users`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Response:**
```json
[
  {
    "id": 1,
    "email": "admin@captcha.local",
    "username": "admin",
    "first_name": "Admin",
    "last_name": "User",
    "is_active": true,
    "is_admin": true,
    "is_verified": true,
    "created_at": "2025-11-13T17:00:00.000Z",
    "updated_at": "2025-11-13T17:00:00.000Z"
  },
  {
    "id": 2,
    "email": "test@captcha.local",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "is_active": true,
    "is_admin": false,
    "is_verified": true,
    "created_at": "2025-11-13T17:01:00.000Z",
    "updated_at": null
  }
]
```

---

## Using with cURL

```bash
# 1. Login and get token
TOKEN=$(curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@captcha.local&password=admin123" \
  | jq -r '.access_token')

# 2. Get all users
curl -X GET http://127.0.0.1:8000/auth/admin/users \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

---

## Using in Frontend (JavaScript/React)

```javascript
// Get token from localStorage
const token = localStorage.getItem("token");

// Fetch all users
const response = await fetch("http://127.0.0.1:8000/auth/admin/users", {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`,
  },
});

if (response.ok) {
  const users = await response.json();
  console.log("All users:", users);

  // Example: Display user count
  console.log(`Total users: ${users.length}`);

  // Example: Filter admins
  const admins = users.filter(u => u.is_admin);
  console.log(`Admin users: ${admins.length}`);

  // Example: Filter verified users
  const verified = users.filter(u => u.is_verified);
  console.log(`Verified users: ${verified.length}`);
}
```

---

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique user ID |
| `email` | string | User's email address |
| `username` | string | Username |
| `first_name` | string | First name (can be null) |
| `last_name` | string | Last name (can be null) |
| `is_active` | boolean | Whether account is active |
| `is_admin` | boolean | Whether user is an admin |
| `is_verified` | boolean | Whether email is verified |
| `created_at` | datetime | When account was created |
| `updated_at` | datetime | Last update time (can be null) |

**Note:** `hashed_password` is NOT included for security reasons.

---

## Features

✅ **Admin-only access** - Regular users get 403 Forbidden
✅ **Ordered by recency** - Newest users appear first
✅ **Complete user data** - All user fields except password
✅ **Works with existing auth** - Uses same token system

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```
**Cause:** Missing or invalid token

**Fix:** Login again to get fresh token

---

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```
**Cause:** User is not an admin

**Fix:** Login with admin credentials

---

## Security Notes

🔒 **Admin Only** - Only users with `is_admin=true` can access this endpoint

🔒 **No Passwords** - Response never includes password hashes

🔒 **Token Required** - Must be authenticated to call

🔒 **Token Expiry** - Tokens expire after 30 minutes, need to re-login

---

## Common Use Cases

### 1. Admin Dashboard
Display total user count and recent signups

### 2. User Management
List all users for admin to view/manage

### 3. Analytics
Count verified users, active users, admin users, etc.

### 4. Debugging
Check what users exist in the system during development

---

## Example Admin Dashboard Stats

```javascript
const response = await fetch("/auth/admin/users", {
  headers: { "Authorization": `Bearer ${token}` }
});

const users = await response.json();

const stats = {
  total: users.length,
  admins: users.filter(u => u.is_admin).length,
  verified: users.filter(u => u.is_verified).length,
  active: users.filter(u => u.is_active).length,
  recentSignups: users.slice(0, 5), // First 5 (most recent)
};

console.log(stats);
```

---

## Testing

### Quick Test
```bash
# Run in terminal
curl -X GET http://127.0.0.1:8000/auth/admin/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Expected Response
- Status: `200 OK`
- Body: Array of user objects
- Ordered: Newest first

---

## Endpoint Location

**File:** `backend/api/routes/auth.py`

**Line:** 144-151

```python
@router.get("/admin/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get all users in the system (admin only)"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users
```

---

## Summary

✅ **Implemented:** Admin endpoint to get all users
✅ **Secure:** Admin-only access
✅ **Simple:** Just `GET /auth/admin/users`
✅ **Complete:** Returns all user data (except password)
✅ **Ready:** Available now at `http://127.0.0.1:8000/auth/admin/users`

You can now view all users in your system! 🎉
