-- order_view.sql
-- List orders for a user
SELECT o.order_id, o.order_date, o.total_amount, o.order_status,
       pm.method_name, ci.full_name AS recipient_name, ci.address AS shipping_address
FROM "order" o
JOIN payment_method pm ON o.payment_method_id = pm.payment_method_id
JOIN contact_info ci ON o.contact_id = ci.contact_id
WHERE o.buyer_id = $1 AND o.is_deleted = FALSE
ORDER BY o.order_date DESC;

-- Get order detail by ID
SELECT o.*, pm.method_name, ci.full_name AS recipient_name, ci.phone_number, ci.address AS shipping_address,
       v.code AS voucher_code,
       v.discount_value,
       (v.discount_type = 1) AS is_percentage,
       array_agg(od.product_id) as product_ids,
       array_agg(od.quantity) as quantities,
       array_agg(od.price_at_purchase) as prices,
       array_agg(od.subtotal) as subtotals
FROM "order" o
JOIN payment_method pm ON o.payment_method_id = pm.payment_method_id
JOIN contact_info ci ON o.contact_id = ci.contact_id
LEFT JOIN voucher v ON o.voucher_id = v.voucher_id
LEFT JOIN order_detail od ON o.order_id = od.order_id
WHERE o.order_id = $1 AND o.is_deleted = FALSE
GROUP BY o.order_id, pm.method_name, ci.full_name, ci.phone_number, ci.address, v.code, v.discount_value, v.discount_type;