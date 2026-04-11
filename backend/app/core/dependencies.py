from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.core.security import decode_token
from app.models import User
from typing import Optional, List

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# ==================== Authentication ====================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = decode_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).options(joinedload(User.role)).filter(User.user_id == token_data.user_id).first()
    if user is None or user.is_deleted or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_optional(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not token:
        return None
    
    token_data = decode_token(token)
    
    if token_data is None:
        return None
    
    user = db.query(User).options(joinedload(User.role)).filter(User.user_id == token_data.user_id).first()
    if user is None or user.is_deleted or not user.is_active:
        return None
    
    return user


# ==================== Authorization ====================

def check_user_role(required_roles: List[int]):
    """Check if user has one of the required roles"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.user_roles in required_roles:
            return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have permission. Required roles: {required_roles}"
        )
    
    return role_checker


def check_admin(user: User = Depends(get_current_user)) -> User:
    """Check if user is admin (role_id = 1)"""
    if user.user_roles != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cút! Chỉ Admin mới được vào đây!"
        )
    return user


def check_moderator(user: User = Depends(get_current_user)) -> User:
    """Check if user is moderator or admin (role_id = 2 or 1)"""
    if user.user_roles not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cút! Chỉ Moderator hoặc Admin mới được vào đây!"
        )
    return user


# Aliases for backward compatibility
get_current_admin = check_admin
get_current_moderator = check_moderator


def check_seller(user: User = Depends(get_current_user)) -> User:
    """Check if user can sell (has seller role/is not purely customer)"""
    # In this system, any verified user can be a seller
    # You might want to add additional checks here
    return user


# ==================== Business Logic ====================

def check_user_is_seller(user: User = Depends(get_current_user)):
    """Check if user is a seller (has listing products)"""
    # This can be checked by verifying user has products
    return user


def check_user_is_not_product_seller(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Check that user is not the seller of the product (for ordering)"""
    from app.models import Product
    
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.seller_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot order your own products"
        )
    
    return current_user
