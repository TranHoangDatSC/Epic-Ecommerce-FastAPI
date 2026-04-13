-- seed.sql
-- Insert users with properly hashed passwords
INSERT INTO "user" (username, email, password_hash, random_key, full_name, phone_number, address, email_verified, trust_score, avatar_url) 
VALUES 
('admin', 'admin@oldshop.com', crypt('admin123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Quản trị viên', '0123456789', '123A Sài Gòn', TRUE, NULL, '/media/users/user_1_admin.png'),
('mod1', 'mod1@gmail.com', crypt('mod123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Trần Kim lộc', '0987654321', '123A Trà Vinh', TRUE, NULL, '/media/users/user_2_mod1.png'),
('user1', 'user1@gmail.com', crypt('user123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Nguyễn Văn An', '0111111111', '123A Vĩnh Long', TRUE, 100.0, '/media/users/user_3_user1.png'),
('user2', 'user2@gmail.com', crypt('user123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Đoàn Thị Chí', '0222222222', '123A Sóc Trăng', TRUE, 100.0, '/media/users/user_3_user2.png');
INSERT INTO user_role (user_id, role_id) VALUES
(1, 1), -- admin as Admin
(2, 2), -- mod1 as Mod
(3, 3), -- user1 as User
(4, 3); -- user2 as User