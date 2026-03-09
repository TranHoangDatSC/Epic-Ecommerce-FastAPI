-- order_import.sql
-- Insert new order
INSERT INTO "order" (buyer_id, contact_id, payment_method_id, total_amount)
VALUES ($1, $2, $3, $4);

-- Insert order with details
WITH new_order AS (
    INSERT INTO "order" (buyer_id, contact_id, payment_method_id, total_amount)
    VALUES (1, 1, 1, 100.00)
    RETURNING order_id
)
INSERT INTO order_detail (order_id, product_id, seller_id, purchased_price, quantity)
SELECT order_id, 1, 2, 50.00, 2 FROM new_order;