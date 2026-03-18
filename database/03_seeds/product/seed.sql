-- seed.sql
INSERT INTO product (seller_id, category_id, title, description, price, quantity, weight_grams, dimensions, condition_rating, warranty_months, status) VALUES
(4, 1, 'Laptop cũ Dell Inspiron 15', 'Laptop Dell Inspiron 15 đã qua sử dụng, cấu hình Core i5, RAM 8GB, SSD 256GB, màn hình 15.6 inch. Còn bảo hành 6 tháng.', 8500000.00, 3, 2200, '35x24x2 cm', 8, 6, 1),
(4, 1, 'iPhone 12 Pro Max 256GB', 'iPhone 12 Pro Max màu xanh, dung lượng 256GB, kèm sạc và cáp. Máy còn mới 95%, không trầy xước.', 18500000.00, 1, 228, '16x7.8x0.7 cm', 9, 12, 1),
(4, 8, 'Tai nghe Sony WH-1000XM4', 'Tai nghe chống ồn Sony WH-1000XM4, màu đen, kèm hộp và cáp. Đã sử dụng 1 năm, còn như mới.', 4500000.00, 2, 254, '30x26x7 cm', 9, 24, 1),
(4, 3, 'Áo khoác mùa đông', 'Áo khoác len dày, size L, màu đen. Đã giặt sạch, không có hư hỏng.', 350000.00, 5, 800, NULL, 7, 0, 1),
(4, 7, 'Tội ác và Hình phạt', 'Tác phẩm hiện sinh nổi tiếng nhất của Dostoevsky.', 800000.00, 1, 3500, '25x18x10 cm', 8, 0, 1);
