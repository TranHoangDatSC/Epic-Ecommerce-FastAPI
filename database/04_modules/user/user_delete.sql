-- user_delete.sql
-- Soft delete user (recommended)
UPDATE "user"
SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE user_id = $1;

-- Hard delete user (use with caution, may violate FK constraints)
-- DELETE FROM "user" WHERE user_id = $1;