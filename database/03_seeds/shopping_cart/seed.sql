-- seed.sql
-- Create shopping carts for all users with role_id = 3 (regular users)
-- This ensures each user automatically has a shopping cart

INSERT INTO shopping_cart (user_id, last_updated) VALUES
(3, CURRENT_TIMESTAMP),  -- user1
(4, CURRENT_TIMESTAMP);  -- user2
