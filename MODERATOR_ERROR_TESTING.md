# Moderator Creation - Comprehensive Error Testing Guide

## All Error Cases Covered

### 1. Missing Required Fields

#### 1.1 Missing username
**Request:**
```bash
POST /api/v1/admin/moderators
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "Pass123456",
  "full_name": "Test User"
}
```
**Expected Response (400):**
```json
{
  "detail": "Field 'username' is required and cannot be empty"
}
```

#### 1.2 Missing email
**Request:**
```bash
{
  "username": "testuser",
  "password": "Pass123456",
  "full_name": "Test User"
}
```
**Expected Response (400):**
```json
{
  "detail": "Field 'email' is required and cannot be empty"
}
```

#### 1.3 Missing password
**Expected Response (400):**
```json
{
  "detail": "Field 'password' is required and cannot be empty"
}
```

#### 1.4 Missing full_name
**Expected Response (400):**
```json
{
  "detail": "Field 'full_name' is required and cannot be empty"
}
```

---

### 2. Invalid Field Types

#### 2.1 Username not string
**Request:**
```json
{
  "username": 123,
  "email": "test@example.com",
  "password": "Pass123456",
  "full_name": "Test User"
}
```
**Expected Response (400):**
```json
{
  "detail": "Username must be a string"
}
```

#### 2.2 Email not string
**Expected Response (400):**
```json
{
  "detail": "Email must be a string"
}
```

#### 2.3 Password not string
**Expected Response (400):**
```json
{
  "detail": "Password must be a string"
}
```

#### 2.4 Full name not string
**Expected Response (400):**
```json
{
  "detail": "Full name must be a string"
}
```

---

### 3. Field Length Validation

#### 3.1 Username too short
**Request:**
```json
{
  "username": "ab",
  "email": "test@example.com",
  "password": "Pass123456",
  "full_name": "Test User"
}
```
**Expected Response (400):**
```json
{
  "detail": "Username must be between 3 and 50 characters (got 2)"
}
```

#### 3.2 Username too long (>50 chars)
**Expected Response (400):**
```json
{
  "detail": "Username must be between 3 and 50 characters (got 51)"
}
```

#### 3.3 Email invalid format
**Request:**
```json
{
  "username": "testuser",
  "email": "notanemail",
  "password": "Pass123456",
  "full_name": "Test User"
}
```
**Expected Response (400):**
```json
{
  "detail": "Invalid email format"
}
```

#### 3.4 Password too short
**Request:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "abc",
  "full_name": "Test User"
}
```
**Expected Response (400):**
```json
{
  "detail": "Password must be at least 6 characters (got 3)"
}
```

#### 3.5 Full name too long
**Expected Response (400):**
```json
{
  "detail": "Full name must be between 1 and 100 characters (got 101+)"
}
```

---

### 4. Duplicate Data Errors

#### 4.1 Username already exists
**Request:**
```json
{
  "username": "existingmod",
  "email": "newmod@example.com",
  "password": "Pass123456",
  "full_name": "New Moderator"
}
```
**Expected Response (400):**
```json
{
  "detail": "Username 'existingmod' already exists"
}
```

#### 4.2 Email already exists
**Request:**
```json
{
  "username": "newmod2",
  "email": "existing@example.com",
  "password": "Pass123456",
  "full_name": "New Moderator"
}
```
**Expected Response (400):**
```json
{
  "detail": "Email 'existing@example.com' already exists"
}
```

#### 4.3 Duplicate key error (database level)
**Expected Response (400):**
```json
{
  "detail": "Username 'testuser' already exists (duplicate key error)"
}
```

---

### 5. Authentication & Authorization Errors

#### 5.1 Missing authentication token
**Request (no Authorization header):**
```bash
POST /api/v1/admin/moderators
Content-Type: application/json

{...}
```
**Expected Response (401):**
```json
{
  "detail": "Not authenticated"
}
```

#### 5.2 Invalid token
**Request:**
```bash
Authorization: Bearer invalid.token.here
```
**Expected Response (401):**
```json
{
  "detail": "Invalid or expired token"
}
```

#### 5.3 Expired token
**Expected Response (401):**
```json
{
  "detail": "Invalid or expired token"
}
```

#### 5.4 User not admin (non-admin token)
**Expected Response (403):**
```json
{
  "detail": "Cút ngay!"
}
```

#### 5.5 Inactive admin account
**Expected Response (400):**
```json
{
  "detail": "Your admin account is not active"
}
```

---

### 6. Data Processing Errors

#### 6.1 Schema conversion error
**Response (400):**
```json
{
  "detail": "Error processing moderator data: ..."
}
```

#### 6.2 Password hashing error
**Response (400):**
```json
{
  "detail": "Error hashing password: ..."
}
```

#### 6.3 Unique key generation error
**Response (400):**
```json
{
  "detail": "Error generating unique key: ..."
}
```

---

### 7. Database Errors

#### 7.1 Database connection error
**Response (500):**
```json
{
  "detail": "Internal server error - Unexpected error: ..."
}
```

#### 7.2 Transaction rollback error
**Response (400 or 500):**
```json
{
  "detail": "Commit error - integrity violation: ..."
}
```

#### 7.3 Random key collision
**Response (400):**
```json
{
  "detail": "Random key collision - please try again"
}
```

---

### 8. Success Cases

#### 8.1 Valid moderator creation
**Request:**
```json
{
  "username": "newmod2024",
  "email": "newmod2024@oldshop.com",
  "password": "SecurePass123",
  "full_name": "New Moderator",
  "phone_number": "0987654321",
  "address": "123 Test Street"
}
```
**Expected Response (200):**
```json
{
  "user_id": 10,
  "username": "newmod2024",
  "email": "newmod2024@oldshop.com",
  "full_name": "New Moderator",
  "phone_number": "0987654321",
  "address": "123 Test Street",
  "role_id": 2,
  "is_active": true,
  "is_deleted": false,
  "created_at": "2024-04-06T10:00:00",
  "updated_at": null,
  "last_login": null,
  "email_verified": false,
  "trust_score": null
}
```

#### 8.2 Without optional fields
**Request:**
```json
{
  "username": "simplemod",
  "email": "simplemod@oldshop.com",
  "password": "Pass123456",
  "full_name": "Simple Moderator"
}
```
**Expected Response (200):**
```json
{
  "user_id": 11,
  "username": "simplemod",
  "email": "simplemod@oldshop.com",
  "full_name": "Simple Moderator",
  "phone_number": null,
  "address": null,
  "role_id": 2,
  "is_active": true,
  "is_deleted": false,
  "created_at": "2024-04-06T10:05:00",
  "updated_at": null,
  "last_login": null,
  "email_verified": false,
  "trust_score": null
}
```

---

## Testing Checklist

- [ ] Test all missing required fields (4 tests)
- [ ] Test invalid field types (4 tests)
- [ ] Test field length validation (5 tests)
- [ ] Test duplicate username/email (2 tests)
- [ ] Test auth errors (5 tests)
- [ ] Test data processing errors (3 tests)
- [ ] Test database errors (3 tests)
- [ ] Test success cases (2 tests)

**Total: 28 test cases**

---

## Notes

1. **Error Logging**: All errors are logged with details for debugging
2. **Transaction Rollback**: All errors trigger database rollback
3. **Validation Order**: 
   - First: Required field validation
   - Then: Type validation
   - Then: Length validation
   - Then: Format validation (email)
   - Then: Uniqueness check
   - Finally: Database operations

4. **Admin Status Check**: Validates admin account is active before processing
5. **Sanitized Logging**: Passwords are never logged
6. **Clear Error Messages**: All errors include specific info about what failed
