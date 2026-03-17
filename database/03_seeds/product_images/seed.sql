-- Product Images Seed Data
-- This file inserts sample product images for the first 5 products

INSERT INTO product_image (product_id, image_url, alt_text, is_primary, display_order) VALUES
(1, '/static/products/prod_1_1_laptop.jpg', 'Dell Inspiron 15 Laptop - Front View', TRUE, 1),
(2, '/static/products/prod_2_1_phone.jpg', 'iPhone 12 Pro Max - Front View', TRUE, 1),
(3, '/static/products/prod_3_1_headphone.jpg', 'Sony WH-1000XM4 Headphones', TRUE, 1),
(4, '/static/products/prod_4_1_coat.jpg', 'Winter Coat - Front View', TRUE, 1),
(5, '/static/products/prod_5_1_crimeandpunishmentbook.jpg', 'Crime and Punishment Book Cover', TRUE, 1);