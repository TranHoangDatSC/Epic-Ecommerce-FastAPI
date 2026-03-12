from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate, UserDetailResponse
from app.core.dependencies import get_current_user, check_admin
from app.crud.user import crud_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserDetailResponse:
    """
    Get current authenticated user's information with roles
    """
    return UserDetailResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        address=current_user.address,
        is_active=current_user.is_active,
        is_deleted=current_user.is_deleted,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login,
        email_verified=current_user.email_verified,
        roles=[
            {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "description": role.description,
                "is_deleted": role.is_deleted,
                "created_at": role.created_at
            }
            for role in current_user.user_roles
        ]
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update current authenticated user's profile information
    """
    updated_user = crud_user.update(db, db_obj=current_user, obj_in=user_update)
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
) -> UserResponse:
    """Get user by ID (public endpoint)"""
    user = crud_user.get_by_user_id(db, user_id=user_id)
    
    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
) -> list[UserResponse]:
    """
    List all users (Admin only).
    
    Requires admin role.
    """
    users = crud_user.get_active_users(db, skip=skip, limit=limit)
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    admin_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a user (Admin only).
    
    Soft deletes the user (sets is_deleted = True).
    """
    user = crud_user.get_by_user_id(db, user_id=user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_deleted = True
    db.add(user)
    db.commit()
