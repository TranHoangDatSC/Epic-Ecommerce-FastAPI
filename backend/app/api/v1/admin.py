from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, models
from app.database import get_db
from app.core.dependencies import get_current_admin
from app.crud import admin as crud_admin
from app.crud.moderator import moderator as crud_moderator

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


# ==================== Moderator Management ====================

@router.get("/moderators", response_model=List[schemas.UserResponse])
def list_moderators(
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """List all moderators (Admin only)"""
    return crud_moderator.get_moderators(db, include_deleted=include_deleted)


@router.post("/moderators", response_model=schemas.UserResponse)
def create_moderator(
    moderator_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """Create a new moderator (Admin only)"""
    import traceback
    import logging

    logger = logging.getLogger(__name__)
    
    try:
        # Log incoming request
        logger.info(f"Admin {admin.email} (ID: {admin.user_id}) attempting to create moderator")
        
        # Validate admin is active
        if not admin.is_active or admin.is_deleted:
            logger.warning(f"Inactive admin {admin.email} attempted to create moderator")
            raise ValueError("Your admin account is not active")

        # Validate required fields for moderator
        if not moderator_data.username:
            logger.warning("Moderator creation failed: username is required")
            raise ValueError("Username is required for moderator creation")

        if not moderator_data.email:
            logger.warning("Moderator creation failed: email is required")
            raise ValueError("Email is required for moderator creation")

        if not moderator_data.password:
            logger.warning("Moderator creation failed: password is required")
            raise ValueError("Password is required for moderator creation")

        if not moderator_data.full_name:
            logger.warning("Moderator creation failed: full_name is required")
            raise ValueError("Full name is required for moderator creation")

        # Convert schema to dict and add role
        try:
            moderator_dict = moderator_data.model_dump()
        except Exception as e:
            logger.error(f"Error converting moderator data to dict: {str(e)}")
            raise ValueError(f"Error processing moderator data: {str(e)}")

        moderator_dict['role_id'] = 2

        # Log sanitized data (without password)
        log_data = {k: v for k, v in moderator_dict.items() if k != 'password'}
        logger.info(f"Creating moderator with data: {log_data}")

        # Create moderator
        try:
            new_moderator = crud_admin.create_moderator(db, moderator_dict, admin.user_id)
            logger.info(f"Successfully created moderator: {new_moderator.username} (ID: {new_moderator.user_id})")
        except ValueError as e:
            # ValueError from CRUD layer (validation error)
            logger.warning(f"Validation error creating moderator: {str(e)}")
            raise
        except Exception as e:
            # Other database or unexpected errors
            logger.error(f"Unexpected error in CRUD layer: {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            raise ValueError(f"Database error: {str(e)}")

        # Validate response can be created
        try:
            response = schemas.UserResponse.model_validate(new_moderator)
            logger.info(f"Successfully validated moderator response for user ID: {new_moderator.user_id}")
            return response
        except Exception as e:
            logger.error(f"Error validating moderator response: {str(e)}")
            raise ValueError(f"Error preparing response: {str(e)}")

    except ValueError as e:
        # Validation error - return 400
        error_detail = str(e)
        logger.warning(f"Moderator creation validation error: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=error_detail
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(f"Unexpected error in create_moderator endpoint: {error_msg}")
        traceback.print_exc()
        logger.error(f"Full traceback above")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Internal server error - {error_msg}"
        )



@router.patch("/moderators/{user_id}/status", response_model=schemas.UserResponse)
def toggle_moderator_status(
    user_id: int,
    status_update: schemas.UserLockRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """Lock or unlock a moderator account (Admin only)"""
    try:
        is_active = status_update.action == "unlock"
        updated_moderator = crud_moderator.toggle_moderator_status(
            db,
            user_id=user_id,
            is_active=is_active,
            reason=status_update.reason,
            admin_id=admin.user_id
        )
        return schemas.UserResponse.model_validate(updated_moderator)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
