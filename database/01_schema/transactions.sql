-- transactions.sql
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