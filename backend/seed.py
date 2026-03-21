#!/usr/bin/env python3
"""
Seed sample data for OldShop SQLite database
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine
from app.models import *

def seed_data():
    """Seed sample data"""
    # Create tables
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Create roles
        admin_role = Role(role_name="Admin", description="Administrator")
        mod_role = Role(role_name="Mod", description="Moderator")
        user_role = Role(role_name="User", description="Regular user")

        db.add_all([admin_role, mod_role, user_role])
        db.commit()

        # Create users
        admin = User(
            username="admin",
            email="admin@oldshop.com",
            password_hash="$2b$12$Y9POr3uNdDBMMPCfq/HAH.53c/W2Lkf577hLLpE/fYFHm.3hSsIoS", # admin123
            random_key="admin_key",
            full_name="Quản trị viên",
            phone_number="0123456789",
            address="123A Sài Gòn",
            is_active=True,
            email_verified=True
        )

        mod1 = User(
            username="mod1",
            email="mod1@gmail.com",
            password_hash="$2b$12$fUbT2uWKVgYZkdwFokTs4uyfCxv1NV0/wmWmuUVUnA4NNkBWc4t3.", # mod123
            random_key="mod1_key",
            full_name="Người duyệt một",
            phone_number="0987654321",
            address="123A Trà Vinh",
            is_active=True,
            email_verified=True
        )

        user1 = User(
            username="user1",
            email="user1@gmail.com",
            password_hash="$2b$12$XIvfr7x62eelLYMGyJ5G7OdiEtgn99Tx5Vk62Ku.LqdYOciKtoWXG", # user123
            random_key="user1_key",
            full_name="Người dùng một",
            phone_number="0111111111",
            address="123A Vĩnh Long",
            is_active=True,
            email_verified=True,
            trust_score=100.0
        )

        user2 = User(
            username="user2",
            email="user2@gmail.com",
            password_hash="$2b$12$XIvfr7x62eelLYMGyJ5G7OdiEtgn99Tx5Vk62Ku.LqdYOciKtoWXG", # user123
            random_key="user2_key",
            full_name="Người bán một",
            phone_number="0222222222",
            address="123A Sóc Trăng",
            is_active=True,
            email_verified=True,
            trust_score=100.0
        )

        db.add_all([admin, mod1, user1, user2])
        db.commit()

        # Create user roles
        db.add_all([
            UserRole(user_id=admin.user_id, role_id=admin_role.role_id),
            UserRole(user_id=mod1.user_id, role_id=mod_role.role_id),
            UserRole(user_id=user1.user_id, role_id=user_role.role_id),
            UserRole(user_id=user2.user_id, role_id=user_role.role_id)
        ])
        db.commit()

        # Create categories
        electronics = Category(name="Electronics", description="Electronic devices")
        clothing = Category(name="Clothing", description="Clothing and fashion")
        books = Category(name="Books", description="Books and literature")

        db.add_all([electronics, clothing, books])
        db.commit()

        # Create products
        laptop = Product(
            seller_id=user2.user_id,
            category_id=electronics.category_id,
            title="Laptop cũ Dell Inspiron 15",
            description="Laptop Dell Inspiron 15 đã qua sử dụng, cấu hình Core i5, RAM 8GB, SSD 256GB, màn hình 15.6 inch. Còn bảo hành 6 tháng.",
            price=8500000.00,
            quantity=3,
            status=1,  # approved
            view_count=10
        )

        iphone = Product(
            seller_id=user2.user_id,
            category_id=electronics.category_id,
            title="iPhone 12 Pro Max 256GB",
            description="iPhone 12 Pro Max màu xanh, dung lượng 256GB, kèm sạc và cáp. Máy còn mới 95%, không trầy xước.",
            price=18500000.00,
            quantity=1,
            status=1,
            view_count=25
        )

        headphones = Product(
            seller_id=user2.user_id,
            category_id=electronics.category_id,
            title="Tai nghe Sony WH-1000XM4",
            description="Tai nghe chống ồn Sony WH-1000XM4, màu đen, kèm hộp và cáp. Đã sử dụng 1 năm, còn như mới.",
            price=4500000.00,
            quantity=2,
            status=1,
            view_count=15
        )

        coat = Product(
            seller_id=user2.user_id,
            category_id=clothing.category_id,
            title="Áo khoác mùa đông",
            description="Áo khoác len dày, size L, màu đen. Đã giặt sạch, không có hư hỏng.",
            price=350000.00,
            quantity=5,
            status=1,
            view_count=8
        )

        book = Product(
            seller_id=user2.user_id,
            category_id=books.category_id,
            title="Tội ác và Hình phạt",
            description="Tác phẩm hiện sinh nổi tiếng nhất của Dostoevsky.",
            price=800000.00,
            quantity=1,
            status=1,
            view_count=5
        )

        db.add_all([laptop, iphone, headphones, coat, book])
        db.commit()

        # Create product images
        db.add_all([
            ProductImage(
                product_id=laptop.product_id,
                image_url="/static/products/laptop1.jpg",
                alt_text="Dell Laptop front",
                is_primary=True,
                display_order=1
            ),
            ProductImage(
                product_id=iphone.product_id,
                image_url="/static/products/iphone1.jpg",
                alt_text="iPhone 12 Pro Max",
                is_primary=True,
                display_order=1
            ),
            ProductImage(
                product_id=headphones.product_id,
                image_url="/static/products/headphones1.jpg",
                alt_text="Sony WH-1000XM4",
                is_primary=True,
                display_order=1
            ),
            ProductImage(
                product_id=coat.product_id,
                image_url="/static/products/coat1.jpg",
                alt_text="Winter coat",
                is_primary=True,
                display_order=1
            ),
            ProductImage(
                product_id=book.product_id,
                image_url="/static/products/book1.jpg",
                alt_text="Crime and Punishment book",
                is_primary=True,
                display_order=1
            )
        ])
        db.commit()

        # Create shopping carts for users with role_id = 3
        from app.models import ShoppingCart
        shopping_carts = [
            ShoppingCart(user_id=user1.user_id),
            ShoppingCart(user_id=user2.user_id)
        ]
        db.add_all(shopping_carts)
        db.commit()

        print("✅ Database seeded successfully!")
        print(f"Created {db.query(Product).count()} products")
        print(f"Created {db.query(Category).count()} categories")
        print(f"Created {db.query(User).count()} users")
        print(f"Created {db.query(ShoppingCart).count()} shopping carts")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()