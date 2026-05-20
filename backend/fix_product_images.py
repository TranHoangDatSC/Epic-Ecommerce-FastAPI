"""
Script: fix_product_images.py
Map ảnh từ backend/media/products/ vào đúng product_id trong DB
Chạy: python fix_product_images.py (từ thư mục backend/)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.models import Product, ProductImage
from sqlalchemy.orm import Session

# ---- Map keyword (lowercase) → (img1, img2) ----
IMAGE_MAP = [
    (["laptop", "dell", "inspiron"],    "prod_1_1_laptop.jpg",                    "prod_1_2_laptop.jpg"),
    (["iphone", "phone", "12 pro"],     "prod_2_1_phone.jpg",                     "prod_2_2_phone.jpg"),
    (["headphone", "sony", "wh-"],      "prod_3_1_headphone.jpg",                 "prod_3_2_headphone.jpg"),
    (["khoác", "coat", "áo"],           "prod_4_1_coat.jpg",                      "prod_4_2_coat.jpg"),
    (["tội ác", "hình phạt", "crime",
      "punishment", "dostoyevsky"],     "prod_5_1_crimeandpunishmentbook.jpg",    "prod_5_2_crimeandpunishmentbook.jpg"),
    (["bếp", "electric", "stove",
      "bếp điện"],                      "prod_6_1_electricstove.jpg",             "prod_6_2_electricstove.jpg"),
    (["bể cá", "fish", "tank",
      "thuỷ tinh"],                     "prod_7_1_fishtank.jpg",                  "prod_7_2_fishtank.jpg"),
    (["sneaker", "giày"],               "prod_8_1_oldsneakers.jpg",               "prod_8_2_oldsneakers.jpg"),
    (["sofa", "ghế", "bộ ghế"],         "prod_9_1_oldsofaset.jpg",                "prod_9_2_oldsofaset.jpg"),
    (["tủ lạnh", "fridge", "lạnh"],     "prod_10_1_oldfridge.jpg",                "prod_10_2_oldfridge.jpg"),
    (["loa", "speaker"],                "prod_11_1_oldspeakerset.jpg",            "prod_11_2_oldspeakerset.jpg"),
    (["máy ảnh", "camera", "ảnh"],      "prod_12_1_oldcamera.jpg",                "prod_12_2_oldcamera.jpg"),
    (["áo sơ mi", "sơ mi", "shirt"],    "prod_13_1_oldshirt.jpg",                 "prod_13_2_oldshirt.jpg"),
    (["đèn", "lamp", "ngủ"],            "prod_14_1_oldlamb.jpg",                  "prod_14_2_oldlamb.jpg"),
    (["giày tây", "tây"],               "prod_15_1_oldshoes.jpg",                 "prod_15_2_oldshoes.jpg"),
    (["flycam", "drone"],               "prod_16_1_olddrone.jpg",                 "prod_16_2_olddrone.jpg"),
    (["điện thoại", "dien thoai"],      "prod_18_1_dien-thoai-qua-tay.jpg",       None),
    (["quạt", "senko"],                 "prod_19_1_quat-senko-cu.jpg",            None),
    (["robot", "hút bụi"],              "prod_20_1_robot-hut-bui.jpg",            None),
]

# Fallback mặc định nếu không match
DEFAULT_IMG = "prod_1_1_laptop.jpg"


def get_images_for(title: str):
    t = title.lower()
    for keywords, img1, img2 in IMAGE_MAP:
        if any(kw in t for kw in keywords):
            return img1, img2
    return DEFAULT_IMG, None


def main():
    db: Session = SessionLocal()
    try:
        # Lấy tất cả products không có ảnh
        products_no_img = (
            db.query(Product)
            .filter(Product.is_deleted == False)
            .all()
        )
        # Lọc những product thực sự chưa có ảnh
        no_img = [p for p in products_no_img if len(p.product_images) == 0]

        print(f"Tổng products: {len(products_no_img)}")
        print(f"Products chưa có ảnh: {len(no_img)}")

        if not no_img:
            print("✅ Tất cả products đã có ảnh!")
            return

        added = 0
        for product in no_img:
            img1, img2 = get_images_for(product.title)

            # Thêm ảnh chính
            pi1 = ProductImage(
                product_id=product.product_id,
                image_url=f"/media/products/{img1}",
                alt_text=f"{product.title} - Ảnh 1",
                is_primary=True,
                display_order=1
            )
            db.add(pi1)

            # Thêm ảnh phụ nếu có
            if img2:
                pi2 = ProductImage(
                    product_id=product.product_id,
                    image_url=f"/media/products/{img2}",
                    alt_text=f"{product.title} - Ảnh 2",
                    is_primary=False,
                    display_order=2
                )
                db.add(pi2)

            added += 1
            if added % 50 == 0:
                print(f"  Đã xử lý {added}/{len(no_img)}...")

        db.commit()
        print(f"\n✅ Đã thêm ảnh cho {added} products!")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
