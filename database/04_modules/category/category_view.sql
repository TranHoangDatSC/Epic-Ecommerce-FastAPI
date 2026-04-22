-- category_view.sql
-- List all active categories
SELECT category_id, category_name, description, created_at
FROM category
WHERE is_deleted = FALSE
ORDER BY category_name;

-- Get category detail by ID
SELECT category_id, category_name, description, created_at
FROM category
WHERE category_id = $1 AND is_deleted = FALSE;