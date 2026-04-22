-- product_delete.sql
-- Soft delete product (recommended)
UPDATE product
SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE product_id = $1;

-- Hard delete product (use with caution)
-- DELETE FROM product WHERE product_id = $1;