from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import verify_password, create_access_token
from app.crud.user import crud_user
from app.models import User, ShoppingCart
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter(prefix="/auth", tags=["auth"])


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
    user = db.query(User).filter(User.email == email).first()

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
    role_ids = [user.role_id]
    
    # Create access token
    access_token_expires = timedelta(minutes=30)  # Default 30 minutes
    access_token = create_access_token(
        data={
            "user_id": user.user_id,
            "username": user.email,
            "role_id": user.role_id  # Trả về số nguyên 1, 2 hoặc 3
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


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    # Debug: In ra xem thằng user này có gì mà sập
    print(f"DEBUG USER ID: {current_user.user_id}")
    
    # Nếu model User của ný không có role_id, hãy lấy từ quan hệ role (nếu có)
    if not hasattr(current_user, 'role_id') or current_user.role_id is None:
        current_user.role_id = 3 # Gán tạm để cứu đói
        
    return current_user