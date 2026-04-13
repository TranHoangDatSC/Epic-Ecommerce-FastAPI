from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app import models, schemas
from app.models import User
from app.schemas import UserResponse, UserUpdate, UserDetailResponse
from app.core.dependencies import get_current_user, check_admin
from app.crud.user import crud_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserDetailResponse:
    """
    Get current authenticated user's information with roles
    """
    # Check if user has role_id = 3 (seller)
    has_seller_role = any(role.role_id == 3 for role in current_user.user_roles)
    role_list = [ur.role for ur in current_user.user_roles]
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
        trust_score=current_user.trust_score if has_seller_role else None,
        roles=role_list
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

@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_in: UserUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return crud_user.update_user(db, db_user=current_user, user_in=user_in)

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
    
    # Check if user has role_id = 3 (seller)
    has_seller_role = any(role.role_id == 3 for role in user.user_roles)
    
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        address=user.address,
        is_active=user.is_active,
        is_deleted=user.is_deleted,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
        email_verified=user.email_verified,
        trust_score=user.trust_score if has_seller_role else None
    )


@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
) -> list[UserResponse]:
    # Dùng hàm mới đã JOIN dữ liệu
    users = crud_user.get_active_users_with_roles(db, skip=skip, limit=limit)
    
    result = []
    for user in users:
        has_seller_role = any(role.role_id == 3 for role in user.user_role)
        
        # Tạo object response kèm danh sách roles
        user_res = UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            phone_number=user.phone_number,
            address=user.address,
            is_active=user.is_active,
            is_deleted=user.is_deleted,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            email_verified=user.email_verified,
            trust_score=user.trust_score if has_seller_role else None,
            roles=[r.role for r in user.user_role if r.role] # Gán roles ở đây
        )
        result.append(user_res)
    return result


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

@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud_user.update_user(db, db_user=current_user, user_in=user_in)

# ==================== User Contact Info ====================

@router.get("/me/contacts", response_model=list[schemas.ContactInfoResponse])
async def get_my_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[schemas.ContactInfoResponse]:
    """Get all contact information for current user"""
    contacts = db.query(models.ContactInfo).filter(
        models.ContactInfo.user_id == current_user.user_id,
        models.ContactInfo.is_deleted == False
    ).order_by(models.ContactInfo.is_default.desc(), models.ContactInfo.created_at.desc()).all()
    return contacts


@router.post("/me/contacts", response_model=schemas.ContactInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_in: schemas.ContactInfoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.ContactInfoResponse:
    """Add new contact information"""
    # If this is the first contact, make it default
    contact_count = db.query(models.ContactInfo).filter(
        models.ContactInfo.user_id == current_user.user_id,
        models.ContactInfo.is_deleted == False
    ).count()
    
    is_default = contact_in.is_default
    if contact_count == 0:
        is_default = True
        
    # If setting as default, unset others
    if is_default:
        db.query(models.ContactInfo).filter(
            models.ContactInfo.user_id == current_user.user_id
        ).update({"is_default": False})
        
    db_contact = models.ContactInfo(
        **contact_in.dict(exclude={"is_default"}),
        user_id=current_user.user_id,
        is_default=is_default
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.post("/me/contacts/{contact_id}/set-default", response_model=schemas.ContactInfoResponse)
async def set_default_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.ContactInfoResponse:
    """Set a contact as default"""
    contact = db.query(models.ContactInfo).filter(
        models.ContactInfo.contact_id == contact_id,
        models.ContactInfo.user_id == current_user.user_id,
        models.ContactInfo.is_deleted == False
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    db.query(models.ContactInfo).filter(
        models.ContactInfo.user_id == current_user.user_id
    ).update({"is_default": False})
    
    contact.is_default = True
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/me/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete contact information"""
    contact = db.query(models.ContactInfo).filter(
        models.ContactInfo.contact_id == contact_id,
        models.ContactInfo.user_id == current_user.user_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    contact.is_deleted = True
    db.commit()
    return None
