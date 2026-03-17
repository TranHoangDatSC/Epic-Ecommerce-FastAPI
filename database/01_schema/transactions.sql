-- transactions.sql
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

-- Indexes for performance
CREATE INDEX idx_transaction_order ON transaction(order_id);
CREATE INDEX idx_transaction_user ON transaction(user_id);
CREATE INDEX idx_transaction_status ON transaction(transaction_status);
