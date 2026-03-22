-- 005_add_role_id_to_user.sql
-- Add role_id column to user table

ALTER TABLE "user" ADD COLUMN role_id INT DEFAULT 3 REFERENCES role(role_id);

-- Update existing users to have role_id based on user_roles
UPDATE "user" SET role_id = (
    SELECT role_id FROM user_role WHERE user_role.user_id = "user".user_id LIMIT 1
) WHERE role_id IS NULL;

-- For users without roles, set to 3
UPDATE "user" SET role_id = 3 WHERE role_id IS NULL;