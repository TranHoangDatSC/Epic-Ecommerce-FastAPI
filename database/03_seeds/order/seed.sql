-- seed.sql
-- Sample order
INSERT INTO "order" (buyer_id, contact_id, payment_method_id, voucher_id, total_amount, shipping_fee, discount_amount, final_amount, order_status, shipping_address) VALUES
(3, 1, 1, 1, 8500000.00, 30000.00, 850000.00, 7680000.00, 1, '123 Lac Long Quan, Phuong 10, TP.HCM');

-- Order details
INSERT INTO order_detail (order_id, product_id, quantity, price_at_purchase, subtotal) VALUES
(1, 1, 1, 8500000.00, 8500000.00);

-- Transaction
INSERT INTO transaction (order_id, user_id, payment_method_id, amount, transaction_status, reference_number) VALUES
(1, 3, 1, 7680000.00, 1, 'TXN_' || encode(gen_random_bytes(16), 'hex'));