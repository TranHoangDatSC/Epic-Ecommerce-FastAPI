-- seed.sql
-- Create shopping carts for all users with role_id = 3 (regular users)
-- This ensures each user automatically has a shopping cart

INSERT INTO shopping_cart (user_id, last_updated) VALUES
(3, CURRENT_TIMESTAMP),  -- user1
(4, CURRENT_TIMESTAMP);  -- user2
(8, CURRENT_TIMESTAMP),  -- user3
(9, CURRENT_TIMESTAMP);  -- user4
(10, CURRENT_TIMESTAMP),  -- user5
(11, CURRENT_TIMESTAMP);  -- user6
(12, CURRENT_TIMESTAMP),  -- user7
(13, CURRENT_TIMESTAMP);  -- user8
(14, CURRENT_TIMESTAMP),  -- user9
(15, CURRENT_TIMESTAMP);  -- user10
(16, CURRENT_TIMESTAMP);  -- user11

