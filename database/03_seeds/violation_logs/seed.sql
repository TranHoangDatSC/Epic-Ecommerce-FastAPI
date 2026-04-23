-- violation_logs_seed.sql

INSERT INTO violation_log (user_id, reason, action_taken, created_at) VALUES 
(2, 'Vi phạm quy định đăng bài nhiều lần, spam nội dung không phù hợp', 'DEACTIVATE_MODERATOR', '2026-04-20 08:30:00'),
(15, 'Sử dụng ngôn từ thô tục trong phần đánh giá sản phẩm', 'DEACTIVATE', '2026-04-20 14:15:22'),
(9, 'Nghi vấn gian lận trong giao dịch thanh toán trực tuyến', 'DEACTIVATE', '2026-04-21 09:10:05'),
(12, 'Cung cấp thông tin sản phẩm sai lệch, gây hiểu lầm cho người mua', 'DEACTIVATE', '2026-04-21 16:45:30'),
(2, 'Đã hoàn thành khóa đào tạo lại quy trình kiểm duyệt', 'ACTIVATE_MODERATOR', '2026-04-22 10:00:00'),
(12, 'Người dùng đã giải trình và bổ sung giấy tờ chứng minh nguồn gốc hàng hóa', 'ACTIVATE', '2026-04-22 11:20:00'),
(5, 'Đăng sản phẩm thuộc danh mục cấm của sàn', 'DEACTIVATE', '2026-04-23 07:55:12'),
(8, 'Bị báo cáo 5 lần bởi các người dùng khác nhau về thái độ phục vụ', 'ADMIN_ACTION: LOCK', '2026-04-23 08:20:45'),
(11, 'Thực hiện hành vi buff đơn ảo nhằm tăng uy tín cửa hàng', 'DEACTIVATE', '2026-04-23 13:40:00'),
(14, 'Nghi vấn đăng nhập trái phép từ nhiều địa chỉ IP lạ', 'ADMIN_ACTION: LOCK', '2026-04-23 15:10:11');