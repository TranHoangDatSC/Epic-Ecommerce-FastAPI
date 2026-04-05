# OldShop API Test Suite

This folder contains test scripts for the OldShop E-Commerce API.

## Prerequisites

- Backend server running on `http://localhost:8000`
- Admin account (default: `admin@oldshop.com` / `admin123`)
- Python 3.8+
- `requests` library installed

## Running Tests

### Moderator API Tests

Run the moderator management endpoint tests:

```bash
python tests/test_moderator_api.py
```

### What's Tested

1. **Admin Login**: Authenticate as admin user
2. **List Moderators**: Retrieve all active moderators
3. **Create Moderator**: Create a new moderator with role_id=2
4. **Lock Moderator**: Deactivate a moderator account
5. **Unlock Moderator**: Reactivate a moderator account

## Test Results

Each test outputs color-coded results:

- `[PASS]` - Test passed successfully (green)
- `[FAIL]` - Test failed (red)
- `[WARN]` - Test warning/skipped (yellow)
- `[INFO]` - Information message (blue)

## Exit Codes

- `0` - All tests passed
- `1` - Tests failed or error occurred

## Notes

- Test moderators are created with unique usernames based on timestamp
- Password used in tests: `TestPassword123` (meets 6+ character requirement)
- Tests clean up after themselves when creating resources
