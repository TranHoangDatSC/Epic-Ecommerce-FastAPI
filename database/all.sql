-- ==============================================================================
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
    password_reset_expires TIMESTAMP
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
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sort_order INTEGER DEFAULT 0,
    icon_url VARCHAR(255),
    parent_category_id INTEGER REFERENCES category(category_id)
);

-- Indexes for categories
CREATE INDEX idx_category_name ON category(category_name) WHERE is_deleted = FALSE;
CREATE INDEX idx_category_parent ON category(parent_category_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_category_sort_order ON category(sort_order) WHERE is_deleted = FALSE;

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
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
);

-- Vouchers table
CREATE TABLE voucher (
    voucher_id SERIAL PRIMARY KEY,
    voucher_code VARCHAR(20) NOT NULL UNIQUE,
    discount_value DECIMAL(18, 2) NOT NULL,
    is_percentage BOOLEAN NOT NULL DEFAULT FALSE,
    expiry_date TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    usage_limit INTEGER DEFAULT NULL,
    used_count INTEGER NOT NULL DEFAULT 0,
    min_order_value DECIMAL(18, 2) DEFAULT 0,
    max_discount DECIMAL(18, 2) DEFAULT NULL,
    applicable_categories TEXT,
    created_by INT REFERENCES "user"(user_id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Indexes for vouchers
CREATE UNIQUE INDEX idx_voucher_code_active ON voucher(voucher_code) WHERE is_active = TRUE;
CREATE INDEX idx_voucher_expiry ON voucher(expiry_date) WHERE is_active = TRUE;
CREATE INDEX idx_voucher_created_by ON voucher(created_by);

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
    recipient_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id)
);

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
    seller_id INT NOT NULL,
    purchased_price DECIMAL(18, 2) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (order_id) REFERENCES "order"(order_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (seller_id) REFERENCES "user"(user_id)
);

-- Transactions table
CREATE TABLE transaction (
    transaction_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    payment_method_id INT NOT NULL,
    transaction_code VARCHAR(100),
    amount DECIMAL(18, 2) NOT NULL,
    transaction_status SMALLINT NOT NULL,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (order_id) REFERENCES "order"(order_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(payment_method_id)
);

-- Shopping carts table
CREATE TABLE shopping_cart (
    cart_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id)
);

-- Shopping cart items table
CREATE TABLE shopping_cart_item (
    item_id SERIAL PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    added_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES shopping_cart(cart_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);

-- Reviews table
CREATE TABLE review (
    review_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    buyer_id INT NOT NULL,
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment VARCHAR(500),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_review_buyer_product UNIQUE (product_id, buyer_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (buyer_id) REFERENCES "user"(user_id)
);

-- System logs table
CREATE TABLE system_log (
    log_id BIGSERIAL PRIMARY KEY,
    user_id INT,
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id INT,
    description TEXT,
    log_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id)
);

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
    p_action_type VARCHAR(50),
    p_table_name VARCHAR(50),
    p_record_id INT DEFAULT NULL,
    p_description TEXT DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    client_ip INET;
    user_agent TEXT;
BEGIN
    BEGIN
        client_ip := inet_client_addr();
        user_agent := current_setting('request.header.user-agent', TRUE);
    EXCEPTION
        WHEN OTHERS THEN
            client_ip := NULL;
            user_agent := NULL;
    END;
    INSERT INTO system_log (user_id, action_type, table_name, record_id, description, log_time)
    VALUES (p_user_id, UPPER(trim(p_action_type)), LOWER(trim(p_table_name)), p_record_id,
        CASE WHEN p_description IS NOT NULL THEN trim(p_description) WHEN client_ip IS NOT NULL THEN 'IP: ' || client_ip::TEXT ELSE 'System action' END,
        CURRENT_TIMESTAMP);
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

CREATE OR REPLACE FUNCTION get_audit_trail(p_table_name VARCHAR(50), p_record_id INT, p_limit INT DEFAULT 50)
RETURNS TABLE (log_id BIGINT, user_id INT, username VARCHAR(50), action_type VARCHAR(50), description TEXT, log_time TIMESTAMP) AS $$
BEGIN
    RETURN QUERY
    SELECT sl.log_id, sl.user_id, u.username, sl.action_type, sl.description, sl.log_time
    FROM system_log sl
    LEFT JOIN "user" u ON sl.user_id = u.user_id
    WHERE sl.table_name = LOWER(trim(p_table_name)) AND sl.record_id = p_record_id
    ORDER BY sl.log_time DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION clean_old_audit_logs(p_days_old INT DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM system_log WHERE log_time < CURRENT_TIMESTAMP - INTERVAL '1 day' * p_days_old;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    PERFORM log_system_action(NULL, 'MAINTENANCE', 'system_log', NULL, 'Cleaned ' || deleted_count || ' audit log entries older than ' || p_days_old || ' days');
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Business functions
CREATE OR REPLACE FUNCTION calculate_order_total(p_subtotal DECIMAL(18,2), p_voucher_id INT DEFAULT NULL, p_shipping_fee DECIMAL(18,2) DEFAULT 0)
RETURNS DECIMAL(18,2) AS $$
DECLARE
    discount_amount DECIMAL(18,2) := 0;
    voucher_record RECORD;
    final_total DECIMAL(18,2);
BEGIN
    IF p_subtotal < 0 THEN
        RAISE EXCEPTION 'Subtotal cannot be negative';
    END IF;
    IF p_shipping_fee < 0 THEN
        RAISE EXCEPTION 'Shipping fee cannot be negative';
    END IF;
    IF p_voucher_id IS NOT NULL THEN
        SELECT * INTO voucher_record FROM voucher WHERE voucher_id = p_voucher_id AND is_active = TRUE AND expiry_date > CURRENT_TIMESTAMP;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Invalid or expired voucher';
        END IF;
        IF voucher_record.usage_limit IS NOT NULL AND voucher_record.used_count >= voucher_record.usage_limit THEN
            RAISE EXCEPTION 'Voucher usage limit exceeded';
        END IF;
        IF p_subtotal < voucher_record.min_order_value THEN
            RAISE EXCEPTION 'Order value does not meet voucher minimum requirement of %', voucher_record.min_order_value;
        END IF;
        IF voucher_record.is_percentage THEN
            discount_amount := p_subtotal * voucher_record.discount_value / 100;
            IF voucher_record.max_discount IS NOT NULL AND discount_amount > voucher_record.max_discount THEN
                discount_amount := voucher_record.max_discount;
            END IF;
        ELSE
            discount_amount := voucher_record.discount_value;
        END IF;
        discount_amount := LEAST(discount_amount, p_subtotal);
    END IF;
    final_total := GREATEST(p_subtotal - discount_amount + p_shipping_fee, 0);
    RETURN final_total;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION apply_voucher_to_order(p_order_id INT, p_voucher_code VARCHAR(20))
RETURNS DECIMAL(18,2) AS $$
DECLARE
    voucher_record RECORD;
    order_record RECORD;
    discount_amount DECIMAL(18,2) := 0;
    final_total DECIMAL(18,2);
BEGIN
    SELECT * INTO order_record FROM "order" WHERE order_id = p_order_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Order not found';
    END IF;
    SELECT * INTO voucher_record FROM voucher WHERE voucher_code = p_voucher_code;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Voucher not found';
    END IF;
    IF NOT voucher_record.is_active THEN
        RAISE EXCEPTION 'Voucher is not active';
    END IF;
    IF voucher_record.expiry_date < CURRENT_TIMESTAMP THEN
        RAISE EXCEPTION 'Voucher has expired';
    END IF;
    IF order_record.voucher_id IS NOT NULL THEN
        RAISE EXCEPTION 'Order already has a voucher applied';
    END IF;
    discount_amount := calculate_order_total(order_record.total_amount, voucher_record.voucher_id, order_record.shipping_fee) - order_record.total_amount + order_record.discount_amount;
    UPDATE "order" SET voucher_id = voucher_record.voucher_id, discount_amount = discount_amount, final_amount = total_amount - discount_amount + shipping_fee, updated_at = CURRENT_TIMESTAMP WHERE order_id = p_order_id;
    UPDATE voucher SET used_count = used_count + 1, updated_at = CURRENT_TIMESTAMP WHERE voucher_id = voucher_record.voucher_id;
    PERFORM log_system_action(order_record.buyer_id, 'VOUCHER_APPLIED', 'order', p_order_id, 'Applied voucher ' || p_voucher_code || ' with discount ' || discount_amount);
    RETURN discount_amount;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION update_product_status_on_quantity()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantity != OLD.quantity THEN
        IF NEW.quantity = 0 AND OLD.quantity > 0 THEN
            NEW.status := 3;
            NEW.sold_at := CURRENT_TIMESTAMP;
            PERFORM log_system_action(NULL, 'PRODUCT_SOLD_OUT', 'product', NEW.product_id, 'Product marked as sold out (quantity: 0)');
        END IF;
        NEW.updated_at := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE TRIGGER trg_update_product_status
BEFORE UPDATE ON product
FOR EACH ROW
WHEN (OLD.quantity != NEW.quantity)
EXECUTE FUNCTION update_product_status_on_quantity();

CREATE OR REPLACE FUNCTION get_product_status_text(p_status SMALLINT)
RETURNS TEXT AS $$
BEGIN
    RETURN CASE p_status WHEN 0 THEN 'Pending Review' WHEN 1 THEN 'Active' WHEN 2 THEN 'Rejected' WHEN 3 THEN 'Sold Out' ELSE 'Unknown' END;
END;
$$ LANGUAGE plpgsql IMMUTABLE SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION get_order_status_text(p_status SMALLINT)
RETURNS TEXT AS $$
BEGIN
    RETURN CASE p_status WHEN 0 THEN 'Pending' WHEN 1 THEN 'Confirmed' WHEN 2 THEN 'Shipping' WHEN 3 THEN 'Delivered' WHEN 4 THEN 'Cancelled' ELSE 'Unknown' END;
END;
$$ LANGUAGE plpgsql IMMUTABLE SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION get_product_average_rating(p_product_id INT)
RETURNS DECIMAL(3,2) AS $$
DECLARE
    avg_rating DECIMAL(3,2);
BEGIN
    SELECT COALESCE(AVG(rating)::DECIMAL(3,2), 0) INTO avg_rating FROM review WHERE product_id = p_product_id AND is_deleted = FALSE;
    RETURN avg_rating;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION get_user_total_spending(p_user_id INT)
RETURNS DECIMAL(18,2) AS $$
DECLARE
    total_spent DECIMAL(18,2);
BEGIN
    SELECT COALESCE(SUM(final_amount), 0) INTO total_spent FROM "order" WHERE buyer_id = p_user_id AND order_status IN (1, 2, 3) AND is_deleted = FALSE;
    RETURN total_spent;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION get_seller_total_revenue(p_seller_id INT)
RETURNS DECIMAL(18,2) AS $$
DECLARE
    total_revenue DECIMAL(18,2);
BEGIN
    SELECT COALESCE(SUM(od.purchased_price * od.quantity), 0) INTO total_revenue FROM order_detail od JOIN "order" o ON od.order_id = o.order_id WHERE od.seller_id = p_seller_id AND o.order_status IN (1, 2, 3) AND o.is_deleted = FALSE;
    RETURN total_revenue;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Utility functions
CREATE OR REPLACE FUNCTION generate_transaction_code()
RETURNS TEXT AS $$
DECLARE
    timestamp_part TEXT;
    random_part TEXT;
BEGIN
    timestamp_part := TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD_HH24MISS');
    random_part := LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');
    RETURN 'TXN_' || timestamp_part || '_' || random_part;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION format_currency(amount DECIMAL(18,2))
RETURNS TEXT AS $$
BEGIN
    RETURN TO_CHAR(amount, 'FM999,999,999,990') || ' VND';
END;
$$ LANGUAGE plpgsql IMMUTABLE SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION calculate_percentage(part DECIMAL, total DECIMAL)
RETURNS DECIMAL(5,2) AS $$
BEGIN
    IF total = 0 THEN RETURN 0; END IF;
    RETURN ROUND((part / total * 100)::DECIMAL(5,2), 2);
END;
$$ LANGUAGE plpgsql IMMUTABLE SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION get_database_stats()
RETURNS TABLE (table_name TEXT, row_count BIGINT, size_pretty TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT t.table_name::TEXT, c.row_count, pg_size_pretty(pg_total_relation_size(t.table_schema || '.' || t.table_name))::TEXT
    FROM information_schema.tables t
    LEFT JOIN (SELECT schemaname, tablename, n_tup_ins - n_tup_del as row_count FROM pg_stat_user_tables) c
    ON t.table_schema = c.schemaname AND t.table_name = c.tablename
    WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
    ORDER BY c.row_count DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Order detail triggers
CREATE OR REPLACE FUNCTION check_no_self_buying()
RETURNS TRIGGER AS $$
DECLARE
    order_buyer_id INT;
BEGIN
    SELECT buyer_id INTO order_buyer_id FROM "order" WHERE order_id = NEW.order_id;
    IF order_buyer_id = NEW.seller_id THEN
        PERFORM log_system_action(order_buyer_id, 'SELF_BUY_BLOCKED', 'order_detail', NEW.order_detail_id, 'Attempted to buy own product (product_id: ' || NEW.product_id || ')');
        RAISE EXCEPTION 'BUSINESS_RULE_VIOLATION: Người bán không thể tự mua sản phẩm của chính mình!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE TRIGGER trg_no_self_buying
BEFORE INSERT ON order_detail
FOR EACH ROW EXECUTE FUNCTION check_no_self_buying();

CREATE OR REPLACE FUNCTION update_stock_on_order()
RETURNS TRIGGER AS $$
DECLARE
    current_quantity INT;
    order_buyer_id INT;
BEGIN
    SELECT quantity INTO current_quantity FROM product WHERE product_id = NEW.product_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'PRODUCT_NOT_FOUND: Product does not exist';
    END IF;
    IF current_quantity < NEW.quantity THEN
        RAISE EXCEPTION 'INSUFFICIENT_STOCK: Only % items available, requested %', current_quantity, NEW.quantity;
    END IF;
    SELECT buyer_id INTO order_buyer_id FROM "order" WHERE order_id = NEW.order_id;
    UPDATE product SET quantity = quantity - NEW.quantity, updated_at = CURRENT_TIMESTAMP WHERE product_id = NEW.product_id;
    PERFORM log_system_action(order_buyer_id, 'STOCK_DECREASE', 'product', NEW.product_id, 'Stock decreased by ' || NEW.quantity || ' for order ' || NEW.order_id || ' (remaining: ' || (current_quantity - NEW.quantity) || ')');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE TRIGGER trg_update_stock
BEFORE INSERT ON order_detail
FOR EACH ROW EXECUTE FUNCTION update_stock_on_order();

CREATE OR REPLACE FUNCTION update_voucher_usage()
RETURNS TRIGGER AS $$
DECLARE
    voucher_code VARCHAR(20);
BEGIN
    IF NEW.voucher_id IS NOT NULL THEN
        SELECT voucher_code INTO voucher_code FROM voucher WHERE voucher_id = NEW.voucher_id;
        UPDATE voucher SET used_count = used_count + 1, updated_at = CURRENT_TIMESTAMP WHERE voucher_id = NEW.voucher_id;
        PERFORM log_system_action(NEW.buyer_id, 'VOUCHER_USED', 'order', NEW.order_id, 'Voucher ' || voucher_code || ' applied to order');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE TRIGGER trg_update_voucher_usage
AFTER INSERT ON "order"
FOR EACH ROW
WHEN (NEW.voucher_id IS NOT NULL)
EXECUTE FUNCTION update_voucher_usage();

CREATE OR REPLACE FUNCTION validate_order_detail()
RETURNS TRIGGER AS $$
DECLARE
    product_status SMALLINT;
    product_seller_id INT;
BEGIN
    SELECT status, seller_id INTO product_status, product_seller_id FROM product WHERE product_id = NEW.product_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'INVALID_PRODUCT: Product does not exist';
    END IF;
    IF product_status != 1 THEN
        RAISE EXCEPTION 'PRODUCT_NOT_AVAILABLE: Product is not available for purchase (status: %)', get_product_status_text(product_status);
    END IF;
    NEW.seller_id := product_seller_id;
    IF NEW.quantity <= 0 THEN
        RAISE EXCEPTION 'INVALID_QUANTITY: Quantity must be greater than 0';
    END IF;
    IF NEW.purchased_price <= 0 THEN
        RAISE EXCEPTION 'INVALID_PRICE: Price must be greater than 0';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE TRIGGER trg_validate_order_detail
BEFORE INSERT ON order_detail
FOR EACH ROW EXECUTE FUNCTION validate_order_detail();

-- ==============================================================================
-- 4. SEED DATA
-- ==============================================================================

-- Roles
INSERT INTO role (role_name, description) VALUES
('Admin', 'Quản trị viên có quyền cao nhất, quản lý toàn bộ hệ thống'),
('Mod', 'Kiểm duyệt viên có quyền quản lý nội dung và người dùng'),
('User', 'Người dùng thông thường, có quyền mua hàng và tương tác cơ bản');

-- Users with hashed passwords
INSERT INTO "user" (username, email, password_hash, random_key, full_name, phone_number, address, email_verified) VALUES
('admin', 'admin@oldshop.com', crypt('admin123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Administrator', '0123456789', 'Admin Address', TRUE),
('reviewer1', 'mod1@gmail.com', crypt('mod123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Reviewer One', '0987654321', 'Reviewer Address', TRUE),
('user1', 'user1@gmail.com', crypt('user123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'User One', '0111111111', 'User Address', TRUE),
('user2', 'user2@gmail.com', crypt('user123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Seller One', '0222222222', 'Seller Address', TRUE);

-- User roles
INSERT INTO user_role (user_id, role_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 3);

-- Categories
INSERT INTO category (category_name, description, sort_order, icon_url) VALUES
('Đồ điện tử', 'Electronic devices and gadgets', 1, 'electronics.png'),
('Trang trí', 'Decorative items for home', 2, 'decor.png'),
('Quần áo', 'Clothing and apparel', 3, 'clothing.png'),
('Thời trang', 'Fashion accessories', 4, 'fashion.png'),
('Đồ chơi', 'Toys and games', 5, 'toys.png'),
('Đồ gia dụng', 'Household items', 6, 'household.png'),
('Sách cũ', 'Used books and literature', 7, 'books.png'),
('Phụ kiện', 'Accessories and miscellaneous', 8, 'accessories.png');

-- Payment methods
INSERT INTO payment_method (method_name, is_online) VALUES
('COD', FALSE), ('MOMO', TRUE), ('VNPAY', TRUE), ('PAYPAL', TRUE), ('BankTransfer', TRUE);

-- Vouchers
INSERT INTO voucher (voucher_code, discount_value, is_percentage, expiry_date, usage_limit, min_order_value, max_discount, created_by) VALUES
('SAVE10', 10.00, TRUE, '2026-12-31 23:59:59', 100, 100.00, 50.00, 1),
('DISCOUNT50', 50.00, FALSE, '2026-06-30 23:59:59', 50, 200.00, NULL, 1),
('FREESHIP', 5.00, FALSE, '2026-05-01 23:59:59', NULL, 150.00, NULL, 1),
('WELCOME20', 20.00, TRUE, '2026-12-31 23:59:59', 500, 50.00, 100.00, 1);

-- Users
INSERT INTO "user" (username, email, password_hash, random_key, full_name, phone_number, address, email_verified) VALUES
('admin', 'admin@oldshop.com', crypt('admin123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Administrator', '0123456789', 'Admin Address', TRUE),
('reviewer1', 'mod1@gmail.com', crypt('mod123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Reviewer One', '0987654321', 'Reviewer Address', TRUE),
('user1', 'user1@gmail.com', crypt('user123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'User One', '0111111111', 'User Address', TRUE),
('user2', 'user2@gmail.com', crypt('user123', gen_salt('bf', 8)), encode(gen_random_bytes(32), 'hex'), 'Seller One', '0222222222', 'Seller Address', TRUE);

-- User roles
INSERT INTO user_role (user_id, role_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 3);

-- Products
INSERT INTO product (seller_id, category_id, title, description, price, quantity, weight_grams, dimensions, condition_rating, warranty_months) VALUES
(4, 1, 'Laptop cu Dell Inspiron 15', 'Laptop Dell Inspiron 15 da qua su dung, cau hinh Core i5, RAM 8GB, SSD 256GB, man hinh 15.6 inch. Con bao hanh 6 thang.', 8500000.00, 3, 2200, '35x24x2 cm', 8, 6),
(4, 1, 'iPhone 12 Pro Max 256GB', 'iPhone 12 Pro Max mau xanh, dung luong 256GB, kem sac va cap. May con moi 95%, khong tray xuoc.', 18500000.00, 1, 228, '16x7.8x0.7 cm', 9, 12),
(4, 8, 'Tai nghe Sony WH-1000XM4', 'Tai nghe chong on Sony WH-1000XM4, mau den, kem hop va cap. Da su dung 1 nam, con nhu moi.', 4500000.00, 2, 254, '30x26x7 cm', 9, 24),
(4, 3, 'Ao khoac mua dong', 'Ao khoac len day, size L, mau den. Da giat sach, khong co hu hong.', 350000.00, 5, 800, NULL, 7, 0),
(4, 7, 'Toi ac va Hinh phat', 'Tac pham hien sinh noi tieng nhat cua Dostoevsky.', 800000.00, 1, 3500, '25x18x10 cm', 8, 0);

-- Contact info
INSERT INTO contact_info (user_id, recipient_name, phone_number, street_address, city) VALUES
(3, 'Nguyen Van A', '0843001701', '123 Lac Long Quan, Phuong 10', 'TP.HCM'),
(4, 'Tran Thi B', '0912345678', '456 Nguyen Hue, Phuong Ben Nghe', 'TP.HCM');

-- Sample order
INSERT INTO "order" (buyer_id, contact_id, payment_method_id, voucher_id, total_amount, shipping_fee, discount_amount, final_amount, order_status, shipping_address) VALUES
(3, 1, 1, 1, 8500000.00, 30000.00, 850000.00, 7680000.00, 1, '123 Lac Long Quan, Phuong 10, TP.HCM');

-- Order details
INSERT INTO order_detail (order_id, product_id, seller_id, purchased_price, quantity) VALUES
(1, 1, 4, 8500000.00, 1);

-- Transaction
INSERT INTO transaction (order_id, payment_method_id, amount, transaction_status, transaction_code) VALUES
(1, 1, 7680000.00, 1, 'TXN_' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD_HH24MISS') || '_' || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0'));

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