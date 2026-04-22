-- product_view.sql
-- List all active products
SELECT p.product_id, p.title, p.price, p.quantity, p.status, p.created_at,
       c.category_name, u.username as seller_name
FROM product p
JOIN category c ON p.category_id = c.category_id
JOIN "user" u ON p.seller_id = u.user_id
WHERE p.is_deleted = FALSE AND p.status = 1
ORDER BY p.created_at DESC;

-- Get product detail by ID
SELECT p.*, c.category_name, u.username as seller_name,
       array_agg(pi.image_url) as images
FROM product p
JOIN category c ON p.category_id = c.category_id
JOIN "user" u ON p.seller_id = u.user_id
LEFT JOIN product_image pi ON p.product_id = pi.product_id AND pi.is_deleted = FALSE
WHERE p.product_id = $1 AND p.is_deleted = FALSE
GROUP BY p.product_id, c.category_name, u.username;