-- product_import.sql
-- Insert new product
INSERT INTO product (seller_id, category_id, title, description, price, quantity)
VALUES ($1, $2, $3, $4, $5, $6);

-- Insert product with images
WITH new_product AS (
    INSERT INTO product (seller_id, category_id, title, price, quantity)
    VALUES (1, 1, 'New Product', 100.00, 10)
    RETURNING product_id
)
INSERT INTO product_image (product_id, image_url, is_default)
SELECT product_id, 'image1.jpg', TRUE FROM new_product
UNION ALL
SELECT product_id, 'image2.jpg', FALSE FROM new_product;