-- category_update.sql
-- Update category info
UPDATE category
SET category_name = $2, description = $3
WHERE category_id = $1 AND is_deleted = FALSE;

-- Soft delete category
UPDATE category
SET is_deleted = TRUE
WHERE category_id = $1;