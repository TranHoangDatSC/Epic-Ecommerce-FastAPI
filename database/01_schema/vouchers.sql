-- vouchers.sql
CREATE TABLE voucher (
    voucher_id SERIAL PRIMARY KEY,
    voucher_code VARCHAR(20) NOT NULL UNIQUE,
    discount_value DECIMAL(18, 2) NOT NULL,
    is_percentage BOOLEAN NOT NULL DEFAULT FALSE,
    expiry_date TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    usage_limit INTEGER DEFAULT NULL, -- NULL means unlimited
    used_count INTEGER NOT NULL DEFAULT 0,
    min_order_value DECIMAL(18, 2) DEFAULT 0,
    max_discount DECIMAL(18, 2) DEFAULT NULL, -- For percentage vouchers
    applicable_categories TEXT, -- JSON array of category IDs
    created_by INT REFERENCES "user"(user_id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Indexes for performance
CREATE UNIQUE INDEX idx_voucher_code_active ON voucher(voucher_code) WHERE is_active = TRUE;
CREATE INDEX idx_voucher_expiry ON voucher(expiry_date) WHERE is_active = TRUE;
CREATE INDEX idx_voucher_created_by ON voucher(created_by);