-- Migration script to update product image URLs
-- Backup was performed before running this.

BEGIN;

-- Update image_url from /static/ to /media/
UPDATE product_image 
SET image_url = REPLACE(image_url, '/static/', '/media/')
WHERE image_url LIKE '/static/%';

COMMIT;
