-- categories.sql
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

-- Indexes for performance
CREATE INDEX idx_category_name ON category(category_name) WHERE is_deleted = FALSE;
CREATE INDEX idx_category_parent ON category(parent_category_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_category_sort_order ON category(sort_order) WHERE is_deleted = FALSE;