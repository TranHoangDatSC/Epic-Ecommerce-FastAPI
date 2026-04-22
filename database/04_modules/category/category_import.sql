-- category_import.sql
-- Insert new category
INSERT INTO category (category_name, description)
VALUES ($1, $2);

-- Insert sample categories
INSERT INTO category (category_name, description) VALUES
('New Category', 'Description for new category');