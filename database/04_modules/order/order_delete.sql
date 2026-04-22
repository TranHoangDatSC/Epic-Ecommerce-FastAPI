-- order_delete.sql
-- Soft delete order (recommended)
UPDATE "order"
SET is_deleted = TRUE
WHERE order_id = $1;

-- Hard delete order (use with caution)
-- DELETE FROM "order" WHERE order_id = $1;