from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DECIMAL, DateTime, 
    ForeignKey, TIMESTAMP, CheckConstraint, Index, SmallInteger, func
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Role(Base):
    """Role model - defines user roles (Admin, Mod, User)"""
    __tablename__ = "role"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255))
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_role_name', 'role_name', postgresql_where=(is_deleted == False)),
        Index('idx_role_created_at', 'created_at'),
    )


class User(Base):
    """User model - stores user information"""
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    random_key = Column(String(64), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(15))
    address = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255))
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    trust_score = Column(DECIMAL(5,2), default=0.0, nullable=True)

    # Relationships
    # link to roles assigned to this user.
    # foreign_keys not required since UserRole now only references User once.
    user_roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    products = relationship("Product", foreign_keys="Product.seller_id", back_populates="seller")
    approved_products = relationship("Product", foreign_keys="Product.approved_by", back_populates="approved_by_user")
    orders = relationship("Order", back_populates="buyer")
    contact_info = relationship("ContactInfo", back_populates="user", cascade="all, delete-orphan")
    shopping_cart = relationship("ShoppingCart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="reviewer")
    transactions = relationship("Transaction", back_populates="user")

    __table_args__ = (
        Index('idx_user_username_active', 'username', postgresql_where=(is_deleted == False)),
        Index('idx_user_email_active', 'email', postgresql_where=(is_deleted == False)),
        Index('idx_user_created_at', 'created_at'),
        Index('idx_user_is_active', 'is_active', postgresql_where=(is_deleted == False)),
        Index('idx_user_email_verified', 'email_verified', postgresql_where=(is_deleted == False)),
    )


class UserRole(Base):
    """UserRole model - maps users to roles (composite primary key)"""
    __tablename__ = "user_role"

    # composite key matches existing SQL schema
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("role.role_id"), primary_key=True)

    # Relationships
    user = relationship(
        "User",
        back_populates="user_roles",
        foreign_keys=[user_id]
    )
    role = relationship("Role", back_populates="user_roles")


class Category(Base):
    """Category model - product categories"""
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("category.category_id"))
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[category_id], backref="children")

    __table_args__ = (
        Index('idx_category_name_active', 'name', postgresql_where=(is_deleted == False)),
        Index('idx_category_parent', 'parent_id', postgresql_where=(is_deleted == False)),
        Index('idx_category_is_active', 'is_active', postgresql_where=(is_deleted == False)),
        Index('idx_category_created_at', 'created_at'),
    )


class Product(Base):
    """Product model - products sold by sellers"""
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("category.category_id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(18, 2), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    view_count = Column(Integer, default=0)
    video_url = Column(String(500))
    status = Column(SmallInteger, default=0, nullable=False, index=True)  # 0: Pending, 1: Approved, 2: Rejected, 3: Sold Out
    reject_reason = Column(String(500))
    approved_by = Column(Integer, ForeignKey("user.user_id"))
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    sold_at = Column(DateTime)
    weight_grams = Column(Integer)
    dimensions = Column(String(50))  # e.g., "10x20x5 cm"
    condition_rating = Column(SmallInteger)  # 1-10 scale
    warranty_months = Column(Integer, default=0)
    transfer_method = Column(SmallInteger, default=1, nullable=False) # 1: Shipping, 2: Meetup

    # Relationships
    seller = relationship("User", foreign_keys=[seller_id], back_populates="products")
    approved_by_user = relationship("User", foreign_keys=[approved_by], back_populates="approved_products")
    category = relationship("Category", back_populates="products")
    product_images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    order_details = relationship("OrderDetail", back_populates="product")
    cart_items = relationship("ShoppingCartItem", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('price >= 0', name='check_product_price'),
        CheckConstraint('quantity >= 0', name='check_product_quantity'),
        CheckConstraint('status IN (0, 1, 2, 3)', name='check_product_status'),
        CheckConstraint('condition_rating BETWEEN 1 AND 10', name='check_condition_rating'),
        CheckConstraint('transfer_method IN (1, 2)', name='check_transfer_method'),
        Index('idx_product_seller', 'seller_id', postgresql_where=(is_deleted == False)),
        Index('idx_product_category', 'category_id', postgresql_where=(is_deleted == False)),
        Index('idx_product_status', 'status', postgresql_where=(is_deleted == False)),
        Index('idx_product_price', 'price', postgresql_where=(is_deleted == False)),
        Index('idx_product_created_at', 'created_at', postgresql_where=(is_deleted == False)),
    )


class ProductImage(Base):
    """ProductImage model - stores product images"""
    __tablename__ = "product_image"

    image_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(255))
    is_primary = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="product_images")


class PaymentMethod(Base):
    """PaymentMethod model - payment methods available"""
    __tablename__ = "payment_method"

    payment_method_id = Column(Integer, primary_key=True, index=True)
    method_name = Column(String(50), unique=True, nullable=False)
    is_online = Column(Boolean, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Relationships
    orders = relationship("Order", back_populates="payment_method")
    transactions = relationship("Transaction", back_populates="payment_method")


class ContactInfo(Base):
    """ContactInfo model - user contact information"""
    __tablename__ = "contact_info"

    contact_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False)
    address = Column(String(255), nullable=False)
    province = Column(String(100))
    district = Column(String(100))
    ward = Column(String(100))
    is_default = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="contact_info")
    orders = relationship("Order", back_populates="contact")


class Order(Base):
    """Order model - customer orders"""
    __tablename__ = "order"

    order_id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contact_info.contact_id"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_method.payment_method_id"), nullable=False)
    voucher_id = Column(Integer, ForeignKey("voucher.voucher_id"))
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_amount = Column(DECIMAL(18, 2), nullable=False)
    shipping_fee = Column(DECIMAL(18, 2), default=0)
    discount_amount = Column(DECIMAL(18, 2), default=0)
    final_amount = Column(DECIMAL(18, 2), nullable=False)
    order_status = Column(SmallInteger, default=0, nullable=False, index=True)  # 0: Pending, 1: Confirmed, 2: Shipping, 3: Delivered, 4: Cancelled
    shipping_address = Column(Text)
    tracking_number = Column(String(100))
    notes = Column(Text)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Relationships
    buyer = relationship("User", back_populates="orders")
    contact = relationship("ContactInfo", back_populates="orders")
    payment_method = relationship("PaymentMethod", back_populates="orders")
    voucher = relationship("Voucher", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="order")

    __table_args__ = (
        CheckConstraint('order_status IN (0, 1, 2, 3, 4)', name='check_order_status'),
        Index('idx_order_buyer', 'buyer_id', postgresql_where=(is_deleted == False)),
        Index('idx_order_status', 'order_status', postgresql_where=(is_deleted == False)),
        Index('idx_order_date', 'order_date', postgresql_where=(is_deleted == False)),
    )


class OrderDetail(Base):
    """OrderDetail model - items in orders"""
    __tablename__ = "order_detail"

    order_detail_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.order_id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(DECIMAL(18, 2), nullable=False)
    subtotal = Column(DECIMAL(18, 2), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="order_details")
    product = relationship("Product", back_populates="order_details")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_order_detail_quantity'),
    )


class ShoppingCart(Base):
    """ShoppingCart model - user shopping carts"""
    __tablename__ = "shopping_cart"

    cart_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), unique=True, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="shopping_cart")
    cart_items = relationship("ShoppingCartItem", back_populates="cart", cascade="all, delete-orphan")


class ShoppingCartItem(Base):
    """ShoppingCartItem model - items in shopping carts"""
    __tablename__ = "shopping_cart_item"

    cart_item_id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("shopping_cart.cart_id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    cart = relationship("ShoppingCart", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_cart_item_quantity'),
    )


class Review(Base):
    """Review model - product reviews"""
    __tablename__ = "review"

    review_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    rating = Column(SmallInteger, nullable=False)  # 1-5
    title = Column(String(255))
    content = Column(Text)
    is_verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")

    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5', name='check_review_rating'),
    )


class Voucher(Base):
    """Voucher model - discount vouchers"""
    __tablename__ = "voucher"

    voucher_id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    discount_type = Column(SmallInteger, default=0)  # 0: Fixed, 1: Percentage
    discount_value = Column(DECIMAL(18, 2), nullable=False)
    max_usage = Column(Integer)
    usage_count = Column(Integer, default=0)
    min_order_amount = Column(DECIMAL(18, 2))
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    orders = relationship("Order", back_populates="voucher")


class Transaction(Base):
    """Transaction model - payment transactions"""
    __tablename__ = "transaction"

    transaction_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.order_id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    payment_method_id = Column(Integer, ForeignKey("payment_method.payment_method_id"), nullable=False)
    amount = Column(DECIMAL(18, 2), nullable=False)
    transaction_status = Column(SmallInteger, default=0)  # 0: Pending, 1: Success, 2: Failed, 3: Refunded
    reference_number = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    payment_method = relationship("PaymentMethod", back_populates="transactions")


class SystemLog(Base):
    """SystemLog model - system audit logs"""
    __tablename__ = "system_log"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_system_log_user', 'user_id'),
        Index('idx_system_log_action', 'action'),
        Index('idx_system_log_created_at', 'created_at'),
    )


class ViolationLog(Base):
    """ViolationLog model - logs for user violations and actions taken"""
    __tablename__ = "violation_log"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    reason = Column(String(500), nullable=False)
    action_taken = Column(String(50), nullable=False)  # BAN, WARNING, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")

    __table_args__ = (
        Index('idx_violation_log_user', 'user_id'),
        Index('idx_violation_log_created_at', 'created_at'),
    )
