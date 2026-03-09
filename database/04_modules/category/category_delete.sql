-- category_delete.sql
-- Soft delete category (recommended)
UPDATE category
SET is_deleted = TRUE
WHERE category_id = $1;

-- Hard delete category (use with caution)
-- DELETE FROM category WHERE category_id = $1;