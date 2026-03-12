-- seed.sql
-- Insert users with properly hashed passwords
INSERT INTO "user" (username, email, password_hash, random_key, full_name, phone_number, address, email_verified) VALUES
('admin', 'admin@oldshop.com', crypt('admin123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Administrator', '0123456789', '123A Sài Gòn', TRUE),
('mod1', 'mod1@gmail.com', crypt('mod123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Reviewer One', '0987654321', '123A Trà Vinh', TRUE),
('user1', 'user1@gmail.com', crypt('user123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'User One', '0111111111', '123A Vĩnh Long', TRUE),
('user2', 'user2@gmail.com', crypt('user123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Seller One', '0222222222', '123A Sóc Trăng', TRUE);

INSERT INTO user_role (user_id, role_id) VALUES
(1, 1), -- admin as Admin
(2, 2), -- mod1 as Mod
(3, 3), -- user1 as User
(4, 3); -- user2 as User