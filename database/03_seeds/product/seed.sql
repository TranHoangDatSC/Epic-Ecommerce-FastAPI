-- seed.sql
INSERT INTO product (seller_id, category_id, title, description, price, quantity, weight_grams, dimensions, condition_rating, warranty_months, status) VALUES
(4, 1, 'Laptop cu Dell Inspiron 15', 'Laptop Dell Inspiron 15 da qua su dung, cau hinh Core i5, RAM 8GB, SSD 256GB, man hinh 15.6 inch. Con bao hanh 6 thang.', 8500000.00, 3, 2200, '35x24x2 cm', 8, 6, 1),
(4, 1, 'iPhone 12 Pro Max 256GB', 'iPhone 12 Pro Max mau xanh, dung luong 256GB, kem sac va cap. May con moi 95%, khong tray xuoc.', 18500000.00, 1, 228, '16x7.8x0.7 cm', 9, 12, 1),
(4, 8, 'Tai nghe Sony WH-1000XM4', 'Tai nghe chong on Sony WH-1000XM4, mau den, kem hop va cap. Da su dung 1 nam, con nhu moi.', 4500000.00, 2, 254, '30x26x7 cm', 9, 24, 1),
(4, 3, 'Ao khoac mua dong', 'Ao khoac len day, size L, mau den. Da giat sach, khong co hu hong.', 350000.00, 5, 800, NULL, 7, 0, 1),
(4, 7, 'Toi ac va Hinh phat', 'Tac pham hien sinh noi tieng nhat cua Dostoevsky.', 800000.00, 1, 3500, '25x18x10 cm', 8, 0, 1);