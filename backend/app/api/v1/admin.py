from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, models
from app.database import get_db
from app.core.dependencies import get_current_admin
from app.crud import admin as crud_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats", response_model=schemas.AdminDashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """Get dashboard stats (Admin only)"""
    return crud_admin.get_admin_stats(db)

@router.get("/feedbacks", response_model=List[schemas.SystemFeedbackResponse])
def list_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """List system feedbacks (Admin only)"""
    return crud_admin.get_feedbacks(db, skip=skip, limit=limit)

@router.patch("/feedbacks/{feedback_id}", response_model=schemas.SystemFeedbackResponse)
def update_feedback(
    feedback_id: int,
    status_update: int = Query(..., ge=0, le=2),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """Update feedback status (Admin only)"""
    db_feedback = crud_admin.update_feedback_status(db, feedback_id, status_update)
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback

@router.get("/users", response_model=List[schemas.UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """List users (Admin only)"""
    # Assuming crud_user logic or simple query
    return crud_admin.get_users_list(db, skip=skip, limit=limit)
