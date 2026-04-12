from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas
from app.database import get_db
from app.crud.moderator import moderator as crud_moderator
from app.core.dependencies import get_current_user, get_current_moderator
from app.core.exceptions import NotFoundException, ValidationException

router = APIRouter(prefix="/moderator", tags=["moderator"])


@router.get("/products/pending", response_model=List[schemas.ProductResponse])
def get_pending_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Get all pending products for approval"""
    return crud_moderator.get_pending_products(db)


@router.patch("/products/{product_id}/status", response_model=schemas.ProductResponse)
def change_product_status(
    product_id: int,
    approval: schemas.ProductApprovalRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Change product status (0: PENDING, 1: APPROVED, 2: REJECTED)"""
    try:
        return crud_moderator.approve_product(
            db,
            product_id=product_id,
            status=approval.status,
            reject_reason=approval.reason,
            moderator_id=current_user.user_id
        )
    except (NotFoundException, ValidationException) as e:
        status_code = status.HTTP_404_NOT_FOUND if isinstance(e, NotFoundException) else status.HTTP_400_BAD_REQUEST
        detail = str(e)
        raise HTTPException(status_code=status_code, detail=detail)


@router.get("/reviews/violations", response_model=List[schemas.ReviewResponse])
def get_violation_reviews(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Get reviews that are potential violations"""
    return crud_moderator.get_violation_reviews(db)


@router.post("/reviews/{review_id}/violation")
def handle_violation_report(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Handle violation report for a review"""
    try:
        crud_moderator.handle_violation_report(
            db,
            review_id=review_id,
            moderator_id=current_user.user_id
        )
        return {"message": "Violation handled successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/users/{user_id}/ban")
def ban_user(
    user_id: int,
    ban_request: schemas.UserBanRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Deactivate a user account (set is_active=False)"""
    try:
        crud_moderator.toggle_user_status(
            db,
            user_id=user_id,
            is_active=False,
            reason=ban_request.reason,
            moderator_id=current_user.user_id
        )
        return {"message": "User deactivated successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/users/{user_id}/unban")
def unban_user(
    user_id: int,
    ban_request: schemas.UserBanRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Activate a user account (set is_active=True)"""
    try:
        crud_moderator.toggle_user_status(
            db,
            user_id=user_id,
            is_active=True,
            reason=ban_request.reason,
            moderator_id=current_user.user_id
        )
        return {"message": "User activated successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users", response_model=List[schemas.UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Get all users with role_id=3 for moderator management."""
    return crud_moderator.get_users_by_role(db, role_id=3)

@router.post("/users/{user_id}/lock-unlock")
def lock_unlock_user(
    user_id: int, 
    lock_request: schemas.UserLockRequest, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_moderator)
):
    """Lock hoặc Unlock user bằng cách gọi đúng hàm đã viết trong CRUD"""
    try:
        # Xác định trạng thái dựa trên action truyền lên
        is_active = (lock_request.action == "unlock") 
        
        # Gọi đúng hàm bạn đã viết trong crud/moderator.py
        user = crud_moderator.toggle_user_status(
            db, 
            user_id=user_id, 
            is_active=is_active, 
            reason=lock_request.reason, 
            moderator_id=current_user.user_id
        )
        
        action_msg = "locked" if lock_request.action == "lock" else "unlocked"
        return {"message": f"User {action_msg} successfully", "user": user}
        
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
@router.get("/violation-logs", response_model=List[schemas.ViolationLogResponse])
def get_violation_logs(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Get violation logs"""
    return crud_moderator.get_violation_logs(db, user_id=user_id)