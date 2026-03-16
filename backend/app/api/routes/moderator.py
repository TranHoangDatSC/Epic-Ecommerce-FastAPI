from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas
from app.database import get_db
from app.crud import moderator as crud_moderator
from app.core.security import get_current_user, get_current_moderator
from app.core.exceptions import NotFoundException, ValidationException

router = APIRouter(prefix="/moderator", tags=["moderator"])


@router.get("/products/pending", response_model=List[schemas.ProductResponse])
def get_pending_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Get all pending products for approval"""
    return crud_moderator.get_pending_products(db)


@router.put("/products/{product_id}/approve", response_model=schemas.ProductResponse)
def approve_product(
    product_id: int,
    approval: schemas.ProductApprovalRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Approve or reject a product"""
    try:
        return crud_moderator.approve_product(
            db,
            product_id=product_id,
            status=approval.status,
            reject_reason=approval.reject_reason,
            moderator_id=current_user.user_id
        )
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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
    """Ban a user account"""
    try:
        crud_moderator.ban_user(
            db,
            user_id=user_id,
            reason=ban_request.reason,
            moderator_id=current_user.user_id
        )
        return {"message": "User banned successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/users/{user_id}/unban")
def unban_user(
    user_id: int,
    ban_request: schemas.UserBanRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Unban a user account"""
    try:
        crud_moderator.unban_user(
            db,
            user_id=user_id,
            reason=ban_request.reason,
            moderator_id=current_user.user_id
        )
        return {"message": "User unbanned successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/users/{user_id}/lock-unlock")
def lock_unlock_user(
    user_id: int,
    lock_request: schemas.UserLockRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator)
):
    """Lock or unlock a user account (only for users with role_id=3)"""
    try:
        user = crud_moderator.lock_unlock_user(
            db,
            user_id=user_id,
            action=lock_request.action,
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