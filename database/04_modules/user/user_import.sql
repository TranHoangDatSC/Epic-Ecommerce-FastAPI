-- user_import.sql
-- Insert new user
INSERT INTO "user" (username, email, password_hash, random_key, full_name, phone_number, address)
VALUES ($1, $2, $3, $4, $5, $6, $7);

-- Insert user with role
WITH new_user AS (
    INSERT INTO "user" (username, email, password_hash, random_key, full_name)
    VALUES ('newuser', 'newuser@example.com', 'hash', 'key', 'New User')
    RETURNING user_id
)
INSERT INTO user_role (user_id, role_id)
SELECT user_id, 3 FROM new_user; -- Role 3 = User