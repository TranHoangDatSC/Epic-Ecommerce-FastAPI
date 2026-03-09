-- seed.sql
INSERT INTO voucher (voucher_code, discount_value, is_percentage, expiry_date, usage_limit, min_order_value, max_discount, created_by) VALUES
('SAVE10', 10.00, TRUE, '2026-12-31 23:59:59', 100, 100.00, 50.00, 1),
('DISCOUNT50', 50.00, FALSE, '2026-06-30 23:59:59', 50, 200.00, NULL, 1),
('FREESHIP', 5.00, FALSE, '2026-05-01 23:59:59', NULL, 150.00, NULL, 1),
('WELCOME20', 20.00, TRUE, '2026-12-31 23:59:59', 500, 50.00, 100.00, 1);