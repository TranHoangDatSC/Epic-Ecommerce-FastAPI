-- product_update.sql
-- Update product info
UPDATE product
SET title = $2, description = $3, price = $4, quantity = $5, updated_at = CURRENT_TIMESTAMP
WHERE product_id = $1 AND is_deleted = FALSE;

-- Update product status (approve/reject)
UPDATE product
SET status = $2, approved_by = $3, reject_reason = $4, updated_at = CURRENT_TIMESTAMP
WHERE product_id = $1;

-- Increment view count
UPDATE product
SET view_count = view_count + 1
WHERE product_id = $1;

-- Soft delete product
UPDATE product
SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE product_id = $1;