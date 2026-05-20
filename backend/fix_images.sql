-- ============================================================
-- Fix: Insert product_image records for all products missing images
-- category mapping:
--   1 = Đồ điện tử  (laptop, phone, loa, máy ảnh, flycam...)
--   2 = Trang trí   (bể cá, sofa, đèn...)
--   3 = Quần áo     (áo khoác, áo sơ mi...)
--   4 = Thời trang  (coat...)
--   5 = Đồ chơi
--   6 = Đồ gia dụng (bếp, tủ lạnh...)
--   7 = Sách cũ
--   8 = Phụ kiện    (giày, tai nghe...)
-- ============================================================

-- Dùng title ILIKE để map chính xác từng loại ảnh
-- Ảnh chính (is_primary = TRUE)
INSERT INTO product_image (product_id, image_url, alt_text, is_primary, display_order)
SELECT
    p.product_id,
    CASE
        -- Điện tử
        WHEN lower(p.title) LIKE '%laptop%'                     THEN '/media/products/prod_1_1_laptop.jpg'
        WHEN lower(p.title) LIKE '%iphone%'
          OR lower(p.title) LIKE '%12 pro%'
          OR (p.category_id=1 AND lower(p.title) LIKE '%phone%')THEN '/media/products/prod_2_1_phone.jpg'
        WHEN lower(p.title) LIKE '%tai nghe%'
          OR lower(p.title) LIKE '%sony%'
          OR lower(p.title) LIKE '%headphone%'                  THEN '/media/products/prod_3_1_headphone.jpg'
        WHEN lower(p.title) LIKE '%loa%'                        THEN '/media/products/prod_11_1_oldspeakerset.jpg'
        WHEN lower(p.title) LIKE '%m%y %nh%'
          OR lower(p.title) LIKE '%camera%'                     THEN '/media/products/prod_12_1_oldcamera.jpg'
        WHEN lower(p.title) LIKE '%flycam%'
          OR lower(p.title) LIKE '%drone%'                      THEN '/media/products/prod_16_1_olddrone.jpg'
        -- Quần áo / Thời trang
        WHEN lower(p.title) LIKE '%kho%c%'                      THEN '/media/products/prod_4_1_coat.jpg'
        WHEN lower(p.title) LIKE '%s%mi%'
          OR lower(p.title) LIKE '%shirt%'                      THEN '/media/products/prod_13_1_oldshirt.jpg'
        -- Trang trí / Nội thất
        WHEN lower(p.title) LIKE '%sofa%'
          OR lower(p.title) LIKE '%gh%%'                        THEN '/media/products/prod_9_1_oldsofaset.jpg'
        WHEN lower(p.title) LIKE '%c%th%y%'
          OR lower(p.title) LIKE '%b% c%%'                      THEN '/media/products/prod_7_1_fishtank.jpg'
        WHEN lower(p.title) LIKE '%%n%'
          AND p.category_id = 2                                 THEN '/media/products/prod_14_1_oldlamb.jpg'
        -- Đồ gia dụng
        WHEN lower(p.title) LIKE '%b%p%'
          OR lower(p.title) LIKE '%stove%'                      THEN '/media/products/prod_6_1_electricstove.jpg'
        WHEN lower(p.title) LIKE '%t%l%nh%'                     THEN '/media/products/prod_10_1_oldfridge.jpg'
        -- Sách
        WHEN p.category_id = 7                                  THEN '/media/products/prod_5_1_crimeandpunishmentbook.jpg'
        -- Phụ kiện / Giày
        WHEN lower(p.title) LIKE '%sneaker%'
          OR (lower(p.title) LIKE '%gi%y%' AND lower(p.title) NOT LIKE '%t%y%')
                                                                THEN '/media/products/prod_8_1_oldsneakers.jpg'
        WHEN lower(p.title) LIKE '%gi%y t%y%'                  THEN '/media/products/prod_15_1_oldshoes.jpg'
        -- Fallback theo category
        WHEN p.category_id = 1  THEN '/media/products/prod_1_1_laptop.jpg'
        WHEN p.category_id = 2  THEN '/media/products/prod_9_1_oldsofaset.jpg'
        WHEN p.category_id = 3  THEN '/media/products/prod_4_1_coat.jpg'
        WHEN p.category_id = 4  THEN '/media/products/prod_4_1_coat.jpg'
        WHEN p.category_id = 5  THEN '/media/products/prod_5_1_crimeandpunishmentbook.jpg'
        WHEN p.category_id = 6  THEN '/media/products/prod_6_1_electricstove.jpg'
        WHEN p.category_id = 7  THEN '/media/products/prod_5_1_crimeandpunishmentbook.jpg'
        WHEN p.category_id = 8  THEN '/media/products/prod_8_1_oldsneakers.jpg'
        ELSE                         '/media/products/prod_1_1_laptop.jpg'
    END,
    p.title || ' - Ảnh chính',
    TRUE,
    1
FROM product p
WHERE p.is_deleted = FALSE
  AND NOT EXISTS (
      SELECT 1 FROM product_image pi WHERE pi.product_id = p.product_id
  );

-- Ảnh phụ (is_primary = FALSE, display_order = 2)
INSERT INTO product_image (product_id, image_url, alt_text, is_primary, display_order)
SELECT
    p.product_id,
    CASE
        WHEN lower(p.title) LIKE '%laptop%'                     THEN '/media/products/prod_1_2_laptop.jpg'
        WHEN lower(p.title) LIKE '%iphone%'
          OR lower(p.title) LIKE '%12 pro%'
          OR (p.category_id=1 AND lower(p.title) LIKE '%phone%')THEN '/media/products/prod_2_2_phone.jpg'
        WHEN lower(p.title) LIKE '%tai nghe%'
          OR lower(p.title) LIKE '%sony%'
          OR lower(p.title) LIKE '%headphone%'                  THEN '/media/products/prod_3_2_headphone.jpg'
        WHEN lower(p.title) LIKE '%loa%'                        THEN '/media/products/prod_11_2_oldspeakerset.jpg'
        WHEN lower(p.title) LIKE '%m%y %nh%'
          OR lower(p.title) LIKE '%camera%'                     THEN '/media/products/prod_12_2_oldcamera.jpg'
        WHEN lower(p.title) LIKE '%flycam%'
          OR lower(p.title) LIKE '%drone%'                      THEN '/media/products/prod_16_2_olddrone.jpg'
        WHEN lower(p.title) LIKE '%kho%c%'                      THEN '/media/products/prod_4_2_coat.jpg'
        WHEN lower(p.title) LIKE '%s%mi%'
          OR lower(p.title) LIKE '%shirt%'                      THEN '/media/products/prod_13_2_oldshirt.jpg'
        WHEN lower(p.title) LIKE '%sofa%'                       THEN '/media/products/prod_9_2_oldsofaset.jpg'
        WHEN lower(p.title) LIKE '%c%th%y%'
          OR lower(p.title) LIKE '%b% c%%'                      THEN '/media/products/prod_7_2_fishtank.jpg'
        WHEN lower(p.title) LIKE '%b%p%'                        THEN '/media/products/prod_6_2_electricstove.jpg'
        WHEN lower(p.title) LIKE '%t%l%nh%'                     THEN '/media/products/prod_10_2_oldfridge.jpg'
        WHEN p.category_id = 7                                  THEN '/media/products/prod_5_2_crimeandpunishmentbook.jpg'
        WHEN lower(p.title) LIKE '%sneaker%'                    THEN '/media/products/prod_8_2_oldsneakers.jpg'
        WHEN lower(p.title) LIKE '%gi%y t%y%'                  THEN '/media/products/prod_15_2_oldshoes.jpg'
        WHEN p.category_id = 1  THEN '/media/products/prod_1_2_laptop.jpg'
        WHEN p.category_id = 2  THEN '/media/products/prod_9_2_oldsofaset.jpg'
        WHEN p.category_id = 3  THEN '/media/products/prod_4_2_coat.jpg'
        WHEN p.category_id = 4  THEN '/media/products/prod_4_2_coat.jpg'
        WHEN p.category_id = 5  THEN '/media/products/prod_5_2_crimeandpunishmentbook.jpg'
        WHEN p.category_id = 6  THEN '/media/products/prod_6_2_electricstove.jpg'
        WHEN p.category_id = 7  THEN '/media/products/prod_5_2_crimeandpunishmentbook.jpg'
        WHEN p.category_id = 8  THEN '/media/products/prod_8_2_oldsneakers.jpg'
        ELSE                         '/media/products/prod_1_2_laptop.jpg'
    END,
    p.title || ' - Ảnh phụ',
    FALSE,
    2
FROM product p
WHERE p.is_deleted = FALSE
  AND (SELECT COUNT(*) FROM product_image pi WHERE pi.product_id = p.product_id) = 1;

-- ============ Báo kết quả ============
SELECT
    'Tổng products' AS thong_ke, COUNT(*)::text AS so_luong
FROM product WHERE is_deleted = FALSE
UNION ALL
SELECT 'Products có ảnh', COUNT(DISTINCT product_id)::text
FROM product_image
UNION ALL
SELECT 'Products CHƯA có ảnh', COUNT(*)::text
FROM product p
WHERE is_deleted = FALSE
  AND NOT EXISTS (SELECT 1 FROM product_image pi WHERE pi.product_id = p.product_id);
