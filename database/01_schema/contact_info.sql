-- contact_info.sql
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