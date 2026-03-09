-- order_update.sql
-- Update order status
UPDATE "order"
SET order_status = $2
WHERE order_id = $1 AND is_deleted = FALSE;

-- Apply voucher to order
UPDATE "order"
SET voucher_id = $2, total_amount = $3
WHERE order_id = $1 AND is_deleted = FALSE;

-- Soft delete order
UPDATE "order"
SET is_deleted = TRUE
WHERE order_id = $1;