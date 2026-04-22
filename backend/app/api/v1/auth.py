from app.core.mail import send_otp_email
from app.schemas import VerifyOTPRequest
from fastapi.openapi.models import EmailStr
from app.schemas import ForgotPasswordRequest
from app.schemas import ResetPasswordRequest
from typing import Optional
from app.core.security import hash_password
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
import secrets as python_secrets
from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse, UserDetailResponse
from app.core.security import verify_password, create_access_token
from app.crud.user import crud_user
from app.models import User, ShoppingCart
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter(prefix="/auth", tags=["auth"])

token = python_secrets.token_urlsafe(32)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user.
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Password (min 6 characters)
    - **full_name**: User's full name
    - **phone_number**: Optional phone number
    - **address**: Optional address
    """
    # Enforce role_id = 3 for public registration
    if getattr(user_in, 'role_id', 3) not in (None, 3):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Role ID can only be 3 (User) for public registration. Only admins can create other roles."
        )
    user_in.role_id = 3
    
    # Auto-generate username from email if not provided
    if not user_in.username:
        import random, string
        base_name = user_in.email.split('@')[0][:40] # max 50 chars total
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        user_in.username = f"{base_name}_{suffix}"
        
        while crud_user.get_by_username(db, username=user_in.username):
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            user_in.username = f"{base_name}_{suffix}"

    # Check if user already exists
    existing_user = crud_user.get_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = crud_user.get_by_email(db, email=user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = crud_user.create(db=db, obj_in=user_in)
    
    # Create shopping cart for new user
    shopping_cart = ShoppingCart(user_id=user.user_id)
    db.add(shopping_cart)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)):
    """
    Login with email and password.

    Note: OAuth2 password flow uses field name "username" in the form, but we
    treat that value as email for this app.
    """
    # Find user by email (OAuth2 form uses username field)
    email = form_data.username
    user = db.query(User).options(joinedload(User.roles)).filter(User.email == email).first()

    if not user:
        print(f"Auth failed: User '{email}' not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.password_hash):
        print(f"Auth failed: Incorrect password for user '{email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_deleted or not user.is_active:
        print(f"Auth failed: User '{user.email}' is inactive or deleted")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Get user roles
    # 1. Lấy danh sách role_id (số nguyên) từ bảng trung gian
    role_ids = [role.role_id for role in user.roles]
    primary_role_id = role_ids[0] if role_ids else 3 

    # 2. Tạo access token với DỮ LIỆU CƠ BẢN (int, str)
    access_token = create_access_token(
        data={
            "user_id": user.user_id,
            "username": user.email,
            "role_id": primary_role_id # Dùng biến số nguyên này
        },
        expires_delta=timedelta(minutes=30)
    )
        
        # Update last login
    user.last_login = __import__('datetime').datetime.utcnow()
    db.add(user)
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=30 * 60  # 30 minutes in seconds
    )


from app.core.dependencies import get_current_user


@router.get("/me", response_model=UserDetailResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    # Debug: In ra xem thằng user này có gì mà sập
    print(f"DEBUG USER ID: {current_user.user_id}")
    
    # Nếu model User của ný không có role_id, hãy lấy từ quan hệ role (nếu có)
    if not hasattr(current_user, 'user_roles') or current_user.user_roles is None:
        current_user.user_roles = 3 # Gán tạm để cứu đói
        
    return current_user

@router.post("/forgot-password", response_model=dict)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Gọi hàm từ crud_user
    token = crud_user.request_password_reset(db, request.email)
    if token:
        print(f"DEBUG: Reset token: {token}")
    return {"message": "Nếu email tồn tại, đường dẫn reset đã được gửi."}

@router.post("/reset-password", response_model=dict)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    success = crud_user.reset_password(db, request.token, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Token không hợp lệ hoặc đã hết hạn"
        )
    return {"message": "Mật khẩu đã được cập nhật thành công"}

@router.post("/forgot-password-otp")
async def forgot_password_otp(email: str, db: Session = Depends(get_db)):
    try:
        otp = crud_user.request_otp_reset(db, email)
        if otp:
            send_otp_email(email, otp)
        return {"message": "Nếu email tồn tại, mã OTP đã được gửi."}
    except Exception as e:
        print(f"LỖI GỬI OTP: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi gửi email")

@router.post("/verify-reset-password")
async def verify_reset_password(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    success = crud_user.verify_otp_and_reset(db, request.email, request.otp, request.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Mã OTP sai hoặc đã hết hạn")
    return {"message": "Mật khẩu đã được cập nhật thành công."}