from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ==================== Auth Schemas ====================

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data payload"""
    user_id: int
    username: str
    role_ids: List[int]


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6)
    role_id: Optional[int] = 3


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    user_id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    email_verified: bool
    trust_score: Optional[float] = None

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """User detail response with roles"""
    roles: List['RoleResponse'] = []


# ==================== Role Schemas ====================

class RoleBase(BaseModel):
    """Base role schema"""
    role_name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Role creation schema"""
    pass


class RoleResponse(RoleBase):
    """Role response schema"""
    role_id: int
    is_deleted: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserRoleAssignment(BaseModel):
    """User role assignment schema"""
    user_id: int
    role_id: int


# ==================== Category Schemas ====================

class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """Category creation schema"""
    pass


class CategoryUpdate(BaseModel):
    """Category update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Category response schema"""
    category_id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Product Schemas ====================

class ProductImageBase(BaseModel):
    """Base product image schema"""
    image_url: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    display_order: int = 0


class ProductImageResponse(ProductImageBase):
    """Product image response"""
    image_id: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Base product schema"""
    category_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    video_url: Optional[str] = None
    weight_grams: Optional[int] = None
    dimensions: Optional[str] = None
    condition_rating: Optional[int] = Field(None, ge=1, le=10)
    warranty_months: int = 0


class ProductCreate(ProductBase):
    """Product creation schema"""
    pass


class ProductUpdate(BaseModel):
    """Product update schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = None
    video_url: Optional[str] = None
    weight_grams: Optional[int] = None
    dimensions: Optional[str] = None
    condition_rating: Optional[int] = None
    warranty_months: Optional[int] = None


class ProductResponse(ProductBase):
    """Product response schema"""
    product_id: int
    seller_id: int
    status: int  # 0: Pending, 1: Approved, 2: Rejected, 3: Sold Out
    reject_reason: Optional[str]
    view_count: int
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime]
    is_approved: bool = False
    product_images: List[ProductImageResponse] = []

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    """Product detail response with images and seller info"""
    product_images: List[ProductImageResponse] = []
    seller: Optional['UserResponse'] = None


# ==================== Payment Method Schemas ====================

class PaymentMethodBase(BaseModel):
    """Base payment method schema"""
    method_name: str = Field(..., min_length=1, max_length=50)
    is_online: bool


class PaymentMethodCreate(PaymentMethodBase):
    """Payment method creation schema"""
    pass


class PaymentMethodResponse(PaymentMethodBase):
    """Payment method response"""
    payment_method_id: int
    is_deleted: bool

    class Config:
        from_attributes = True


# ==================== Contact Info Schemas ====================

class ContactInfoBase(BaseModel):
    """Base contact info schema"""
    full_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., max_length=15)
    address: str = Field(..., max_length=255)
    province: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None


class ContactInfoCreate(ContactInfoBase):
    """Contact info creation schema"""
    is_default: bool = False


class ContactInfoUpdate(BaseModel):
    """Contact info update schema"""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None
    is_default: Optional[bool] = None


class ContactInfoResponse(ContactInfoBase):
    """Contact info response"""
    contact_id: int
    user_id: int
    is_default: bool
    is_deleted: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Shopping Cart Schemas ====================

class ShoppingCartItemBase(BaseModel):
    """Base shopping cart item schema"""
    product_id: int
    quantity: int = Field(..., gt=0)


class ShoppingCartItemCreate(ShoppingCartItemBase):
    """Shopping cart item creation schema"""
    pass


class ShoppingCartItemResponse(ShoppingCartItemBase):
    """Shopping cart item response"""
    cart_item_id: int
    added_at: datetime
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class ShoppingCartResponse(BaseModel):
    """Shopping cart response"""
    cart_id: int
    user_id: int
    last_updated: datetime
    cart_items: List[ShoppingCartItemResponse] = []

    class Config:
        from_attributes = True


# ==================== Order Schemas ====================

class OrderDetailBase(BaseModel):
    """Base order detail schema"""
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderDetailCreate(OrderDetailBase):
    """Order detail creation schema"""
    pass


class OrderDetailResponse(OrderDetailBase):
    """Order detail response"""
    order_detail_id: int
    price_at_purchase: Decimal
    subtotal: Decimal
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base order schema"""
    contact_id: int
    payment_method_id: int
    voucher_id: Optional[int] = None
    shipping_fee: Decimal = Field(default=0, ge=0)
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation schema"""
    order_items: List[OrderDetailCreate]

    @validator('order_items')
    def validate_order_items(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v


class OrderUpdate(BaseModel):
    """Order update schema"""
    order_status: Optional[int] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Order response schema"""
    order_id: int
    buyer_id: int
    order_date: datetime
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    order_status: int  # 0: Pending, 1: Confirmed, 2: Shipping, 3: Delivered, 4: Cancelled
    shipping_address: Optional[str]
    tracking_number: Optional[str]
    is_deleted: bool

    class Config:
        from_attributes = True


class OrderDetailResponse_Extended(OrderResponse):
    """Order detail response with items information"""
    order_details: List[OrderDetailResponse] = []
    buyer: Optional[UserResponse] = None


# ==================== Voucher Schemas ====================

class VoucherBase(BaseModel):
    """Base voucher schema"""
    code: str = Field(..., max_length=50)
    description: Optional[str] = None
    discount_type: int = 0  # 0: Fixed, 1: Percentage
    discount_value: Decimal = Field(..., gt=0)
    max_usage: Optional[int] = None
    min_order_amount: Optional[Decimal] = None
    valid_from: datetime
    valid_to: datetime


class VoucherCreate(VoucherBase):
    """Voucher creation schema"""
    pass


class VoucherUpdate(BaseModel):
    """Voucher update schema"""
    description: Optional[str] = None
    discount_value: Optional[Decimal] = None
    max_usage: Optional[int] = None
    min_order_amount: Optional[Decimal] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class VoucherResponse(VoucherBase):
    """Voucher response"""
    voucher_id: int
    usage_count: int
    is_active: bool
    is_deleted: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Review Schemas ====================

class ReviewBase(BaseModel):
    """Base review schema"""
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None


class ReviewCreate(ReviewBase):
    """Review creation schema"""
    pass


class ReviewUpdate(BaseModel):
    """Review update schema"""
    rating: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None


class ReviewResponse(ReviewBase):
    """Review response"""
    review_id: int
    buyer_id: int
    is_verified_purchase: bool
    helpful_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: bool
    reviewer: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# ==================== Transaction Schemas ====================

class TransactionBase(BaseModel):
    """Base transaction schema"""
    amount: Decimal = Field(..., gt=0)
    reference_number: Optional[str] = None
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Transaction response"""
    transaction_id: int
    order_id: int
    user_id: int
    payment_method_id: int
    transaction_status: int  # 0: Pending, 1: Success, 2: Failed, 3: Refunded
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Update forward references
UserDetailResponse.update_forward_refs()
ProductDetailResponse.update_forward_refs()


# ==================== Moderator Schemas ====================

class ProductApprovalRequest(BaseModel):
    """Product approval request"""
    product_id: Optional[int] = None
    status: int = Field(..., ge=0, le=2)  # 0: Pending, 1: Approved, 2: Rejected
    reason: Optional[str] = Field(None, max_length=500)


class ViolationReportRequest(BaseModel):
    """Violation report request"""
    review_id: int


class UserBanRequest(BaseModel):
    """User ban request"""
    user_id: int
    reason: str = Field(..., max_length=500)


class UserLockRequest(BaseModel):
    """User lock/unlock request"""
    action: str = Field(..., pattern="^(lock|unlock)$")  # lock or unlock
    reason: str = Field(..., max_length=500)


class ViolationLogResponse(BaseModel):
    """Violation log response"""
    log_id: int
    user_id: int
    reason: str
    action_taken: str
    created_at: datetime

    class Config:
        from_attributes = True
