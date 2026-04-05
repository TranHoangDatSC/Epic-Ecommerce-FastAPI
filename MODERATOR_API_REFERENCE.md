# Moderator Creation API Test - Reference Guide

## 1. Login as Admin First

**Request:**
```bash
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@oldshop.com
password=admin123
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## 2. Create Moderator

**Request:**
```bash
POST http://localhost:8000/api/v1/admin/moderators
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "username": "newmod2024",
  "email": "newmod2024@oldshop.com",
  "password": "SecurePass123",
  "full_name": "New Moderator",
  "phone_number": "0123456789",
  "address": "Test Address"
}
```

**Expected Response (200 OK):**
```json
{
  "user_id": 5,
  "username": "newmod2024",
  "email": "newmod2024@oldshop.com",
  "full_name": "New Moderator",
  "phone_number": "0123456789",
  "address": "Test Address",
  "role_id": 2,
  "is_active": true,
  "is_deleted": false,
  "created_at": "2024-04-05T10:30:00",
  "updated_at": null,
  "last_login": null,
  "email_verified": false,
  "trust_score": null,
  "role": {
    "role_id": 2,
    "role_name": "Moderator",
    "description": "Moderator role",
    "is_deleted": false,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

## 3. Common Issues

### Issue: 400 Bad Request - Username is required
**Cause**: Username field is None or empty
**Solution**: Always provide username when creating moderator

### Issue: 400 Bad Request - Username already exists
**Cause**: The username is already taken by another user
**Solution**: Use a unique username

### Issue: 400 Bad Request - Email already exists
**Cause**: The email is already registered
**Solution**: Use a unique email address

### Issue: 403 Forbidden
**Cause**: User token doesn't have admin role (role_id != 1)
**Solution**: Make sure you login as an actual admin user

### Issue: 500 Internal Server Error
**Cause**: Check server console for error details
**Solution**: Look at the error message returned in response and console output

## 4. Fields Reference

| Field | Required | Min | Max | Notes |
|-------|----------|-----|-----|-------|
| username | Yes | 3 | 50 | Must be unique |
| email | Yes | - | 100 | Must be valid email, unique |
| password | Yes | 6 | - | Will be hashed with bcrypt |
| full_name | Yes | 1 | 100 | User's display name |
| phone_number | No | - | 15 | Optional phone number |
| address | No | - | 255 | Optional address |
