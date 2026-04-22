-- user_update.sql
-- Update user profile
UPDATE "user"
SET full_name = $2, phone_number = $3, address = $4, updated_at = CURRENT_TIMESTAMP
WHERE user_id = $1 AND is_deleted = FALSE;

-- Activate/Deactivate user
UPDATE "user"
SET is_active = $2, updated_at = CURRENT_TIMESTAMP
WHERE user_id = $1;

-- Soft delete user
UPDATE "user"
SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE user_id = $1;