INSERT INTO product (seller_id, category_id, title, description, price, quantity, weight_grams, dimensions, condition_rating, warranty_months, status, transfer_method) VALUES
-- [Status 1: Đang bán - Chiếm đa số (11 sản phẩm)]
(3, 1, 'Laptop Dell Inspiron 15', 'Laptop đã qua sử dụng...', 8500000.00, 3, 2200, '35x24x2 cm', 8, 6, 1, 1),
(3, 1, 'iPhone 12 Pro Max 256GB', 'iPhone 12 Pro Max màu xanh...', 18500000.00, 1, 228, '16x7.8x0.7 cm', 9, 12, 1, 1),
(3, 3, 'Áo khoác mùa đông', 'Áo khoác len dày...', 350000.00, 5, 800, NULL, 7, 0, 1, 2),
(3, 7, 'Tội ác và Hình phạt', 'Tác phẩm hiện sinh...', 800000.00, 1, 3500, '25x18x10 cm', 8, 0, 1, 1),
(3, 6, 'Bếp điện cũ', 'Bếp điện gia dụng 2 vòng nhiệt.', 500000.00, 1, 3000, '50x30x10 cm', 7, 0, 1, 1),
(4, 2, 'Bể cá thủy tinh', 'Bể cá cảnh kèm máy lọc mini.', 300000.00, 1, 5000, '40x25x25 cm', 8, 0, 1, 1),
(3, 8, 'Giày sneakers cũ', 'Giày thể thao size 40.', 200000.00, 1, 600, '30x15x10 cm', 6, 0, 1, 2),
(3, 2, 'Bộ sofa cũ', 'Sofa da 3 chỗ ngồi.', 2500000.00, 1, 45000, '200x80x80 cm', 7, 0, 1, 2),
(4, 6, 'Tủ lạnh cũ', 'Tủ lạnh mini 90L.', 1200000.00, 1, 20000, '50x50x80 cm', 8, 3, 1, 2),
(4, 1, 'Bộ loa vi tính', 'Loa 2.1 âm thanh tốt.', 450000.00, 1, 2500, '30x20x20 cm', 8, 0, 1, 1),
(3, 1, 'Máy ảnh cũ', 'Máy ảnh kỹ thuật số.', 1500000.00, 1, 400, '12x8x5 cm', 7, 0, 1, 1),

-- [Status 2: Bị từ chối (2 sản phẩm)]
(3, 3, 'Áo sơ mi cũ', 'Áo sơ mi nam size M.', 100000.00, 2, 200, NULL, 8, 0, 2, 1),
(3, 2, 'Đèn ngủ cũ', 'Đèn bàn cổ điển.', 150000.00, 1, 800, '20x20x30 cm', 9, 0, 2, 1),

-- [Status 3: Hết hàng (1 sản phẩm)]
(3, 8, 'Giày tây cũ', 'Giày da nam size 41.', 300000.00, 1, 700, '32x15x12 cm', 7, 0, 3, 1),

-- [Status 0: Đang chờ duyệt (2 sản phẩm)]
(3, 1, 'Flycam cũ', 'Drone DJI cũ hoạt động tốt.', 5500000.00, 1, 1200, '25x25x10 cm', 9, 6, 0, 1),
(3, 8, 'Tai nghe Sony WH-1000XM4', 'Tai nghe chống ồn...', 4500000.00, 2, 254, '30x26x7 cm', 9, 24, 0, 1);