-- user_view.sql
-- List all users
SELECT user_id, username, email, full_name, phone_number, address, is_active, created_at
FROM "user"
WHERE is_deleted = FALSE
ORDER BY created_at DESC;

-- Get user detail by ID
SELECT u.user_id, u.username, u.email, u.full_name, u.phone_number, u.address, u.is_active, u.created_at,
       array_agg(r.role_name) as roles
FROM "user" u
LEFT JOIN user_role ur ON u.user_id = ur.user_id
LEFT JOIN role r ON ur.role_id = r.role_id
WHERE u.user_id = $1 AND u.is_deleted = FALSE
GROUP BY u.user_id, u.username, u.email, u.full_name, u.phone_number, u.address, u.is_active, u.created_at;