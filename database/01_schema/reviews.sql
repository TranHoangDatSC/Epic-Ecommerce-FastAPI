-- system_logs.sql
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