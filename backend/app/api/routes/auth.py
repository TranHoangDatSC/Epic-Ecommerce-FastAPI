from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import verify_password, create_access_token
from app.crud.user import crud_user
from app.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


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
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Login with username and password.
    
    Returns JWT access token for authentication.
    """
    # Find user by username
    user = crud_user.get_by_username(db, username=credentials.username)
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.is_deleted or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Get user roles
    role_ids = [role.role_id for role in user.user_roles]
    
    # Create access token
    access_token_expires = timedelta(minutes=30)  # Default 30 minutes
    access_token = create_access_token(
        data={
            "user_id": user.user_id,
            "username": user.username,
            "role_ids": role_ids
        },
        expires_delta=access_token_expires
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


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(lambda db=Depends(get_db): Depends(get_db))
) -> UserResponse:
    """Get current authenticated user info"""
    # This needs proper dependency injection
    # Will be fixed in the main route registration
    pass
