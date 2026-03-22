-- =
-- OLD SHOP DATABASE - COMPLETE SETUP SCRIPT
-- ==============================================================================
-- This script creates the entire OldShop PostgreSQL database from scratch
-- Execute this single file to set up everything needed for the system
-- ==============================================================================

-- ==============================================================================
-- 1. DATABASE CONFIGURATION
-- ==============================================================================
-- Set timezone and enable extensions
SET timezone = 'Asia/Ho_Chi_Minh';

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Database settings for better performance
ALTER DATABASE oldshop SET search_path TO public;
SET search_path TO public;

-- Connection and memory settings
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Logging settings
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';
ALTER SYSTEM SET log_statement = 'ddl';
ALTER SYSTEM SET log_duration = on;

-- Autovacuum settings
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_max_workers = 3;
ALTER SYSTEM SET autovacuum_naptime = '20s';
ALTER SYSTEM SET autovacuum_vacuum_threshold = 50;
ALTER SYSTEM SET autovacuum_analyze_threshold = 50;

-- ==============================================================================
-- 2. SCHEMA CREATION
-- ==============================================================================

-- Roles table
CREATE TABLE role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Indexes for roles
CREATE INDEX idx_role_name ON role(role_name) WHERE is_deleted = FALSE;
CREATE INDEX idx_role_created_at ON role(created_at);

-- Users table
CREATE TABLE "user" (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    random_key VARCHAR(64) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15),
    address VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    last_login TIMESTAMP,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    trust_score DECIMAL(5,2) DEFAULT 0.0
);

-- Indexes for users
CREATE UNIQUE INDEX idx_user_username_active ON "user"(username) WHERE is_deleted = FALSE;
CREATE UNIQUE INDEX idx_user_email_active ON "user"(email) WHERE is_deleted = FALSE;
CREATE INDEX idx_user_created_at ON "user"(created_at);
CREATE INDEX idx_user_is_active ON "user"(is_active) WHERE is_deleted = FALSE;
CREATE INDEX idx_user_email_verified ON "user"(email_verified) WHERE is_deleted = FALSE;

-- User roles table
CREATE TABLE user_role (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES "user"(user_id),
    FOREIGN KEY (role_id) REFERENCES role(role_id)
);

-- Categories table
CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id INTEGER REFERENCES category(category_id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Indexes for categories
CREATE UNIQUE INDEX idx_category_name_active ON category(name) WHERE is_deleted = FALSE;
CREATE INDEX idx_category_parent ON category(parent_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_category_is_active ON category(is_active) WHERE is_deleted = FALSE;
CREATE INDEX idx_category_created_at ON category(created_at);

-- Products table
CREATE TABLE product (
    product_id SERIAL PRIMARY KEY,
    seller_id INT NOT NULL,
    category_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(18, 2) NOT NULL CHECK (price >= 0),
    quantity INT NOT NULL CHECK (quantity >= 0),
    view_count INT NOT NULL DEFAULT 0,
    video_url VARCHAR(500),
    status SMALLINT NOT NULL DEFAULT 0 CHECK (status IN (0, 1, 2, 3)),
    reject_reason VARCHAR(500),
    approved_by INT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    sold_at TIMESTAMP,
    weight_grams INTEGER,
    dimensions VARCHAR(50),
    condition_rating SMALLINT CHECK (condition_rating BETWEEN 1 AND 10),
    warranty_months INTEGER DEFAULT 0,
    FOREIGN KEY (seller_id) REFERENCES "user"(user_id),
    FOREIGN KEY (category_id) REFERENCES category(category_id),
    FOREIGN KEY (approved_by) REFERENCES "user"(user_id)
);

-- Indexes for products
CREATE INDEX idx_product_seller ON product(seller_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_product_category ON product(category_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_product_status ON product(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_product_price ON product(price) WHERE is_deleted = FALSE;
CREATE INDEX idx_product_created_at ON product(created_at) WHERE is_deleted = FALSE;
CREATE INDEX idx_product_title ON product USING gin(to_tsvector('english', title)) WHERE is_deleted = FALSE;

-- Product images table
CREATE TABLE product_image (
    image_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    display_order INTEGER NOT NULL DEFAULT 0,
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
);

-- Indexes for product images
CREATE INDEX idx_product_image_product ON product_image(product_id);

-- Vouchers table
CREATE TABLE voucher (
    voucher_id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    discount_type SMALLINT NOT NULL DEFAULT 0,
    discount_value DECIMAL(18, 2) NOT NULL,
    max_usage INT,
    usage_count INT NOT NULL DEFAULT 0,
    min_order_amount DECIMAL(18, 2),
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for vouchers
CREATE UNIQUE INDEX idx_voucher_code_active ON voucher(code) WHERE is_active = TRUE;
CREATE INDEX idx_voucher_valid_to ON voucher(valid_to) WHERE is_active = TRUE;
CREATE INDEX idx_voucher_created_at ON voucher(created_at);

-- Payment methods table
CREATE TABLE payment_method (
    payment_method_id SERIAL PRIMARY KEY,
    method_name VARCHAR(50) NOT NULL UNIQUE,
    is_online BOOLEAN NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- Contact info table
CREATE TABLE contact_info (
    contact_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    address VARCHAR(255) NOT NULL,
    province VARCHAR(100),
    district VARCHAR(100),
    ward VARCHAR(100),
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id)
);

-- Indexes for contact info
CREATE INDEX idx_contact_info_user ON contact_info(user_id);
CREATE INDEX idx_contact_info_default ON contact_info(is_default) WHERE is_deleted = FALSE;

-- Orders table
CREATE TABLE "order" (
    order_id SERIAL PRIMARY KEY,
    buyer_id INT NOT NULL,
    contact_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    voucher_id INT,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(18, 2) NOT NULL,
    shipping_fee DECIMAL(18, 2) DEFAULT 0,
    discount_amount DECIMAL(18, 2) DEFAULT 0,
    final_amount DECIMAL(18, 2) NOT NULL,
    order_status SMALLINT NOT NULL DEFAULT 0 CHECK (order_status IN (0, 1, 2, 3, 4)),
    shipping_address TEXT,
    tracking_number VARCHAR(100),
    notes TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (buyer_id) REFERENCES "user"(user_id),
    FOREIGN KEY (contact_id) REFERENCES contact_info(contact_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(payment_method_id),
    FOREIGN KEY (voucher_id) REFERENCES voucher(voucher_id)
);

-- Indexes for orders
CREATE INDEX idx_order_buyer ON "order"(buyer_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_order_status ON "order"(order_status) WHERE is_deleted = FALSE;
CREATE INDEX idx_order_date ON "order"(order_date) WHERE is_deleted = FALSE;

-- Order details table
CREATE TABLE order_detail (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_at_purchase DECIMAL(18, 2) NOT NULL,
    subtotal DECIMAL(18, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES "order"(order_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);

-- Indexes for order details
CREATE INDEX idx_order_detail_order ON order_detail(order_id);

-- Transactions table
CREATE TABLE transaction (
    transaction_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    transaction_status SMALLINT NOT NULL DEFAULT 0,
    reference_number VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES "order"(order_id),
    FOREIGN KEY (user_id) REFERENCES "user"(user_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(payment_method_id)
);

-- Indexes for transactions
CREATE INDEX idx_transaction_order ON transaction(order_id);
CREATE INDEX idx_transaction_user ON transaction(user_id);
CREATE INDEX idx_transaction_status ON transaction(transaction_status);

-- Shopping carts table
CREATE TABLE shopping_cart (
    cart_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id)
);

-- Shopping cart items table
CREATE TABLE shopping_cart_item (
    cart_item_id SERIAL PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES shopping_cart(cart_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);

-- Indexes for shopping cart items
CREATE INDEX idx_shopping_cart_item_cart ON shopping_cart_item(cart_id);
CREATE INDEX idx_shopping_cart_item_product ON shopping_cart_item(product_id);

-- Reviews table
CREATE TABLE review (
    review_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    buyer_id INT NOT NULL,
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(255),
    content TEXT,
    is_verified_purchase BOOLEAN NOT NULL DEFAULT FALSE,
    helpful_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (buyer_id) REFERENCES "user"(user_id)
);

-- System logs table
CREATE TABLE system_log (
    log_id BIGSERIAL PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id)
);

-- Indexes for system logs
CREATE INDEX idx_system_log_user ON system_log(user_id);
CREATE INDEX idx_system_log_action ON system_log(action);
CREATE INDEX idx_system_log_created_at ON system_log(created_at);

-- Violation logs table
CREATE TABLE violation_log (
    log_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    reason VARCHAR(500) NOT NULL,
    action_taken VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id)
);

-- Indexes for violation logs
CREATE INDEX idx_violation_log_user ON violation_log(user_id);
CREATE INDEX idx_violation_log_created_at ON violation_log(created_at);

-- System feedback table
CREATE TABLE system_feedback (
    feedback_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(user_id) ON DELETE SET NULL,
    guest_email VARCHAR(255),
    subject VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    status SMALLINT DEFAULT 0, -- 0: Pending, 1: Reviewed, 2: Resolved
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for system feedback
CREATE INDEX idx_system_feedback_user ON system_feedback(user_id);
CREATE INDEX idx_system_feedback_status ON system_feedback(status);
CREATE INDEX idx_system_feedback_created_at ON system_feedback(created_at);

-- ==============================================================================
-- 3. FUNCTIONS AND TRIGGERS
-- ==============================================================================

-- Password functions
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
DECLARE
    hashed_password TEXT;
BEGIN
    IF password IS NULL OR length(trim(password)) = 0 THEN
        RAISE EXCEPTION 'Password cannot be empty';
    END IF;
    IF length(password) < 6 THEN
        RAISE EXCEPTION 'Password must be at least 6 characters long';
    END IF;
    hashed_password := crypt(password, gen_salt('bf', 8));
    RETURN hashed_password;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION verify_password(password TEXT, hashed_password TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    is_valid BOOLEAN := FALSE;
BEGIN
    IF password IS NULL OR hashed_password IS NULL THEN
        RETURN FALSE;
    END IF;
    IF crypt(password, hashed_password) = hashed_password THEN
        is_valid := TRUE;
    END IF;
    RETURN is_valid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION generate_random_key()
RETURNS TEXT AS $$
DECLARE
    random_key TEXT;
BEGIN
    random_key := encode(gen_random_bytes(32), 'hex');
    RETURN random_key;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION generate_password_reset_token()
RETURNS TEXT AS $$
DECLARE
    token TEXT;
BEGIN
    token := encode(gen_random_bytes(32), 'base64');
    token := replace(replace(token, '+', '-'), '/', '_');
    token := rtrim(token, '=');
    RETURN token;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION create_user_with_hash(
    p_username VARCHAR(50),
    p_email VARCHAR(100),
    p_password TEXT,
    p_full_name VARCHAR(100),
    p_phone_number VARCHAR(15) DEFAULT NULL,
    p_address VARCHAR(255) DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    new_user_id INTEGER;
    email_regex TEXT := '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
BEGIN
    IF p_username IS NULL OR length(trim(p_username)) = 0 THEN
        RAISE EXCEPTION 'Username cannot be empty';
    END IF;
    IF p_email IS NULL OR length(trim(p_email)) = 0 THEN
        RAISE EXCEPTION 'Email cannot be empty';
    END IF;
    IF p_full_name IS NULL OR length(trim(p_full_name)) = 0 THEN
        RAISE EXCEPTION 'Full name cannot be empty';
    END IF;
    IF NOT (p_email ~ email_regex) THEN
        RAISE EXCEPTION 'Invalid email format';
    END IF;
    IF EXISTS (SELECT 1 FROM "user" WHERE username = trim(p_username) AND is_deleted = FALSE) THEN
        RAISE EXCEPTION 'Username already exists';
    END IF;
    IF EXISTS (SELECT 1 FROM "user" WHERE email = trim(p_email) AND is_deleted = FALSE) THEN
        RAISE EXCEPTION 'Email already exists';
    END IF;
    INSERT INTO "user" (username, email, password_hash, random_key, full_name, phone_number, address, email_verified)
    VALUES (trim(p_username), trim(p_email), hash_password(p_password), generate_random_key(), trim(p_full_name), NULLIF(trim(p_phone_number), ''), NULLIF(trim(p_address), ''), FALSE)
    RETURNING user_id INTO new_user_id;
    PERFORM log_system_action(new_user_id, 'USER_CREATED', 'user', new_user_id, 'User account created');
    RETURN new_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION authenticate_user(p_username_or_email TEXT, p_password TEXT)
RETURNS TABLE (user_id INTEGER, username VARCHAR(50), email VARCHAR(100), full_name VARCHAR(100), is_active BOOLEAN, role_name VARCHAR(50)) AS $$
DECLARE
    user_record RECORD;
    login_successful BOOLEAN := FALSE;
BEGIN
    SELECT u.*, r.role_name INTO user_record
    FROM "user" u
    JOIN user_role ur ON u.user_id = ur.user_id
    JOIN role r ON ur.role_id = r.role_id
    WHERE (u.username = p_username_or_email OR u.email = p_username_or_email)
    AND u.is_deleted = FALSE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid username or password';
    END IF;
    IF NOT user_record.is_active THEN
        RAISE EXCEPTION 'Account is deactivated';
    END IF;
    IF verify_password(p_password, user_record.password_hash) THEN
        login_successful := TRUE;
        UPDATE "user" SET last_login = CURRENT_TIMESTAMP WHERE user_id = user_record.user_id;
        PERFORM log_system_action(user_record.user_id, 'LOGIN_SUCCESS', 'user', user_record.user_id, 'Successful login');
    ELSE
        PERFORM log_system_action(user_record.user_id, 'LOGIN_FAILED', 'user', user_record.user_id, 'Failed login attempt');
        RAISE EXCEPTION 'Invalid username or password';
    END IF;
    RETURN QUERY SELECT user_record.user_id, user_record.username, user_record.email, user_record.full_name, user_record.is_active, user_record.role_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Audit functions
CREATE OR REPLACE FUNCTION log_system_action(
    p_user_id INT,
    p_action VARCHAR(100),
    p_resource_type VARCHAR(50),
    p_resource_id INT DEFAULT NULL,
    p_details TEXT DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    client_ip INET;
BEGIN
    BEGIN
        client_ip := inet_client_addr();
    EXCEPTION
        WHEN OTHERS THEN
            client_ip := NULL;
    END;
    INSERT INTO system_log (user_id, action, resource_type, resource_id, details, ip_address, created_at)
    VALUES (p_user_id, UPPER(trim(p_action)), LOWER(trim(p_resource_type)), p_resource_id,
        trim(p_details), client_ip::VARCHAR(45), CURRENT_TIMESTAMP);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION log_user_login(p_user_id INT, p_ip_address INET DEFAULT NULL, p_user_agent TEXT DEFAULT NULL)
RETURNS VOID AS $$
DECLARE
    login_description TEXT;
BEGIN
    UPDATE "user" SET last_login = CURRENT_TIMESTAMP WHERE user_id = p_user_id AND is_deleted = FALSE;
    login_description := 'User login';
    IF p_ip_address IS NOT NULL THEN
        login_description := login_description || ' from IP: ' || p_ip_address::TEXT;
    END IF;
    IF p_user_agent IS NOT NULL THEN
        login_description := login_description || ' using: ' || substring(p_user_agent, 1, 100);
    END IF;
    PERFORM log_system_action(p_user_id, 'LOGIN', 'user', p_user_id, login_description);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION log_user_logout(p_user_id INT)
RETURNS VOID AS $$
BEGIN
    PERFORM log_system_action(p_user_id, 'LOGOUT', 'user', p_user_id, 'User logout');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION get_audit_trail(p_resource_type VARCHAR(50), p_resource_id INT, p_limit INT DEFAULT 50)
RETURNS TABLE (log_id BIGINT, user_id INT, username VARCHAR(50), action VARCHAR(100), details TEXT, created_at TIMESTAMP) AS $$
BEGIN
    RETURN QUERY
    SELECT sl.log_id, sl.user_id, u.username, sl.action, sl.details, sl.created_at
    FROM system_log sl
    LEFT JOIN "user" u ON sl.user_id = u.user_id
    WHERE sl.resource_type = LOWER(trim(p_resource_type)) AND sl.resource_id = p_resource_id
    ORDER BY sl.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION clean_old_audit_logs(p_days_old INT DEFAULT 180)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM system_log WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * p_days_old;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    PERFORM log_system_action(NULL, 'MAINTENANCE', 'system_log', NULL, 'Cleaned ' || deleted_count || ' audit log entries older than ' || p_days_old || ' days');
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Business functions and triggers
\i 02_functions/all_functions.sql

-- ==============================================================================
-- 4. SEED DATA
-- ==============================================================================
-- ==============================================================================
-- 4. SEED DATA
-- ==============================================================================

-- Roles
INSERT INTO role (role_name, description) VALUES
('Admin', 'Quản trị viên có quyền cao nhất, quản lý toàn bộ hệ thống'),
('Mod', 'Kiểm duyệt viên có quyền quản lý nội dung và người dùng'),
('User', 'Người dùng thông thường, có quyền mua hàng và tương tác cơ bản');

-- Users with hashed passwords
INSERT INTO "user" (username, email, password_hash, random_key, full_name, phone_number, address, email_verified, trust_score) VALUES
('admin', 'admin@oldshop.com', crypt('admin123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Administrator', '0123456789', 'Admin Address', TRUE, NULL),
('reviewer1', 'mod1@gmail.com', crypt('mod123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Reviewer One', '0987654321', 'Reviewer Address', TRUE, NULL),
('user1', 'user1@gmail.com', crypt('user123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'User One', '0111111111', 'User Address', TRUE, 100.0),
('user2', 'user2@gmail.com', crypt('user123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Seller One', '0222222222', 'Seller Address', TRUE, 100.0);

-- User roles
INSERT INTO user_role (user_id, role_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 3);

-- Categories
INSERT INTO category (name, description) VALUES
('Đồ điện tử', 'Electronic devices and gadgets'),
('Trang trí', 'Decorative items for home'),
('Quần áo', 'Clothing and apparel'),
('Thời trang', 'Fashion accessories'),
('Đồ chơi', 'Toys and games'),
('Đồ gia dụng', 'Household items'),
('Sách cũ', 'Used books and literature'),
('Phụ kiện', 'Accessories and miscellaneous');

-- Payment methods
INSERT INTO payment_method (method_name, is_online) VALUES
('COD', FALSE), ('MOMO', TRUE), ('VNPAY', TRUE), ('PAYPAL', TRUE), ('BankTransfer', TRUE);

-- Vouchers
INSERT INTO voucher (code, discount_type, discount_value, max_usage, min_order_amount, valid_from, valid_to, is_active, is_deleted, created_at) VALUES
('SAVE10', 1, 10.00, 100, 100.00, '2024-01-01 00:00:00', '2026-12-31 23:59:59', TRUE, FALSE, CURRENT_TIMESTAMP),
('DISCOUNT50', 0, 50.00, 50, 200.00, '2024-01-01 00:00:00', '2026-06-30 23:59:59', TRUE, FALSE, CURRENT_TIMESTAMP),
('FREESHIP', 0, 5.00, NULL, 150.00, '2024-01-01 00:00:00', '2026-05-01 23:59:59', TRUE, FALSE, CURRENT_TIMESTAMP),
('WELCOME20', 1, 20.00, 500, 50.00, '2024-01-01 00:00:00', '2026-12-31 23:59:59', TRUE, FALSE, CURRENT_TIMESTAMP);

-- Products
INSERT INTO product (seller_id, category_id, title, description, price, quantity, weight_grams, dimensions, condition_rating, warranty_months) VALUES
(4, 1, 'Laptop cu Dell Inspiron 15', 'Laptop Dell Inspiron 15 da qua su dung, cau hinh Core i5, RAM 8GB, SSD 256GB, man hinh 15.6 inch. Con bao hanh 6 thang.', 8500000.00, 3, 2200, '35x24x2 cm', 8, 6),
(4, 1, 'iPhone 12 Pro Max 256GB', 'iPhone 12 Pro Max mau xanh, dung luong 256GB, kem sac va cap. May con moi 95%, khong tray xuoc.', 18500000.00, 1, 228, '16x7.8x0.7 cm', 9, 12),
(4, 8, 'Tai nghe Sony WH-1000XM4', 'Tai nghe chong on Sony WH-1000XM4, mau den, kem hop va cap. Da su dung 1 nam, con nhu moi.', 4500000.00, 2, 254, '30x26x7 cm', 9, 24),
(4, 3, 'Ao khoac mua dong', 'Ao khoac len day, size L, mau den. Da giat sach, khong co hu hong.', 350000.00, 5, 800, NULL, 7, 0),
(4, 7, 'Toi ac va Hinh phat', 'Tac pham hien sinh noi tieng nhat cua Dostoevsky.', 800000.00, 1, 3500, '25x18x10 cm', 8, 0);

-- Product images
INSERT INTO product_image (product_id, image_url, alt_text, is_primary, display_order) VALUES
(1, '/static/products/1_1_dell_laptop.jpg', 'Dell Inspiron 15 front view', TRUE, 1),
(1, '/static/products/1_2_dell_laptop_side.jpg', 'Dell Inspiron 15 side view', FALSE, 2),
(2, '/static/products/2_1_iphone_12_pro_max.jpg', 'iPhone 12 Pro Max front', TRUE, 1),
(2, '/static/products/2_2_iphone_12_pro_max_back.jpg', 'iPhone 12 Pro Max back', FALSE, 2),
(3, '/static/products/3_1_sony_wh1000xm4.jpg', 'Sony WH-1000XM4 headphones', TRUE, 1),
(4, '/static/products/4_1_winter_jacket.jpg', 'Winter jacket front', TRUE, 1),
(5, '/static/products/5_1_crime_and_punishment.jpg', 'Crime and Punishment book cover', TRUE, 1);

-- Contact info
INSERT INTO contact_info (user_id, full_name, phone_number, address) VALUES
(3, 'Nguyen Van A', '0843001701', '123 Lac Long Quan, Phuong 10, TP.HCM'),
(4, 'Tran Thi B', '0912345678', '456 Nguyen Hue, Phuong Ben Nghe, TP.HCM');

-- Sample order
INSERT INTO "order" (buyer_id, contact_id, payment_method_id, voucher_id, total_amount, shipping_fee, discount_amount, final_amount, order_status, shipping_address) VALUES
(3, 1, 1, 1, 8500000.00, 30000.00, 850000.00, 7680000.00, 1, '123 Lac Long Quan, Phuong 10, TP.HCM');

-- Order details
INSERT INTO order_detail (order_id, product_id, price_at_purchase, quantity) VALUES
(1, 1, 8500000.00, 1);

-- Transaction
INSERT INTO transaction (order_id, user_id, payment_method_id, amount, transaction_status, reference_number) VALUES
(1, 3, 1, 7680000.00, 1, 'TXN_' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD_HH24MISS') || '_' || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0'));

-- Shopping carts for users with role_id = 3
INSERT INTO shopping_cart (user_id, last_updated) VALUES
(3, CURRENT_TIMESTAMP),  -- user1
(4, CURRENT_TIMESTAMP);  -- user2

-- ==============================================================================
-- 5. FINAL SETUP
-- ==============================================================================

-- Analyze tables for query optimization
ANALYZE;

-- Create partial index for active products search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_active_search
ON product USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')))
WHERE is_deleted = FALSE AND status = 1;

-- Display setup completion message
DO $$
BEGIN
    RAISE NOTICE '================================================';
    RAISE NOTICE 'OldShop Database Setup Completed Successfully!';
    RAISE NOTICE '================================================';
    RAISE NOTICE 'Version: 2.0.0 - Professional Edition';
    RAISE NOTICE 'Features: Security, Performance, Monitoring, Audit';
    RAISE NOTICE '';
    RAISE NOTICE 'Default login credentials:';
    RAISE NOTICE 'Admin: admin@oldshop.com / admin123';
    RAISE NOTICE 'Mod: mod1@gmail.com / mod123';
    RAISE NOTICE 'User: user1@gmail.com / user123';
    RAISE NOTICE 'Seller: user2@gmail.com / user123';
    RAISE NOTICE '';
    RAISE NOTICE 'Database is ready for use!';
    RAISE NOTICE '================================================';
END $$;

-- ==============================================================================
-- END OF SETUP SCRIPT
-- ==============================================================================