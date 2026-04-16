-- seed.sql
-- Sample order
INSERT INTO "order" (buyer_id, contact_id, payment_method_id, voucher_id, total_amount, shipping_fee, discount_amount, final_amount, order_status, shipping_address) VALUES
(3, 1, 1, 1, 500000, 30000, 50000, 480000, 0, '123 Lê Lợi, Q1'),
(4, 2, 2, NULL, 1200000, 0, 0, 1200000, 0, '45 Nguyễn Huệ, Q1'),
(3, 3, 1, 1, 350000, 30000, 30000, 350000, 1, '10 Pasteur, Q1'),
(4, 4, 2, NULL, 8500000, 0, 0, 8500000, 1, '22 Võ Văn Tần, Q3'),
(3, 5, 1, 1, 200000, 30000, 20000, 210000, 1, '88 CMT8, Q3'),
(4, 6, 1, NULL, 1500000, 30000, 0, 1530000, 0, '12 Điện Biên Phủ, BT'),
(3, 7, 2, 1, 4500000, 0, 500000, 4000000, 1, '50 Nguyễn Đình Chiểu, Q3'),
(4, 8, 1, NULL, 100000, 30000, 0, 130000, 0, '15 NTMK, Q1'),
(3, 9, 2, 1, 300000, 30000, 50000, 280000, 1, '200 Phan Xích Long, PN'),
(4, 10, 1, NULL, 5500000, 0, 0, 5500000, 1, '99 Hoàng Diệu, Q4'),
(3, 11, 1, NULL, 800000, 30000, 0, 830000, 2, '5 Lý Tự Trọng, Q1'),
(4, 12, 2, 1, 2500000, 0, 200000, 2300000, 2, '88 Đinh Tiên Hoàng, Q1'),
(3, 13, 1, NULL, 450000, 30000, 0, 480000, 3, '30 Nguyễn Huệ, Q1'),
(4, 14, 2, NULL, 1200000, 0, 0, 1200000, 3, '120 CMT8, Q10'),
(3, 15, 1, 1, 300000, 30000, 50000, 280000, 2, '45 Lê Văn Sỹ, Q3'),
(4, 1, 2, NULL, 150000, 30000, 0, 180000, 3, '123 Lê Lợi, Q1'),
(3, 2, 1, 1, 18500000, 0, 1000000, 17500000, 3, '45 Nguyễn Huệ, Q1'),
(4, 3, 2, NULL, 500000, 30000, 0, 530000, 2, '10 Pasteur, Q1'),
(3, 4, 1, 1, 200000, 30000, 50000, 180000, 3, '22 Võ Văn Tần, Q3'),
(4, 5, 2, NULL, 600000, 30000, 0, 630000, 2, '88 CMT8, Q3'),
(3, 6, 1, NULL, 100000, 30000, 0, 130000, 4, '12 Điện Biên Phủ, BT'),
(4, 7, 1, NULL, 50000, 30000, 0, 80000, 4, '50 Nguyễn Đình Chiểu, Q3'),
(3, 8, 2, 1, 4500000, 0, 500000, 4000000, 4, '15 NTMK, Q1'),
(4, 9, 1, NULL, 300000, 30000, 0, 330000, 4, '200 Phan Xích Long, PN'),
(3, 10, 1, NULL, 8500000, 0, 0, 8500000, 3, '99 Hoàng Diệu, Q4'),
(4, 11, 2, 1, 250000, 30000, 25000, 255000, 1, '5 Lý Tự Trọng, Q1'),
(3, 12, 1, NULL, 350000, 30000, 0, 380000, 0, '88 Đinh Tiên Hoàng, Q1'),
(4, 13, 2, NULL, 1500000, 0, 0, 1500000, 2, '30 Nguyễn Huệ, Q1'),
(3, 14, 1, 1, 200000, 30000, 20000, 210000, 4, '120 CMT8, Q10'),
(4, 15, 2, NULL, 120000, 30000, 0, 150000, 1, '45 Lê Văn Sỹ, Q3');
-- Order details & Transaction
DO $$
DECLARE
    i INT;
BEGIN
    FOR i IN 2..31 LOOP
        -- Order Details
        INSERT INTO order_detail (order_id, product_id, quantity, price_at_purchase, subtotal)
        VALUES (i, (i % 16) + 1, 1, 100000, 100000);
        
        -- Transaction
        INSERT INTO transaction (order_id, user_id, payment_method_id, amount, transaction_status, reference_number)
        VALUES (i, (CASE WHEN i % 2 = 0 THEN 1 ELSE 2 END), 1, 100000, 1, 'TXN_' || encode(gen_random_bytes(16), 'hex'));
    END LOOP;
END $$;