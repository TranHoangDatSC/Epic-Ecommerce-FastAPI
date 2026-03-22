from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import Optional
from app import schemas, models
from app.database import get_db
from app.core.security import get_current_user
from app.crud import admin as crud_admin
from jose import JWTError, jwt
from app.core.security import oauth2_scheme, decode_token

router = APIRouter(prefix="/system", tags=["system"])

def log_feedback_email(guest_email: str, subject: str):
    """Background task to simulate sending email for guest feedback"""
    print(f"\n[EMAIL LOG - GUEST FEEDBACK]")
    print(f"To: contact@oldshop.com")
    print(f"From: {guest_email}")
    print(f"Subject: {subject}")
    print(f"Message: New feedback received from guest user.")
    print("-" * 30 + "\n")

@router.post("/feedback", response_model=schemas.SystemFeedbackResponse, status_code=status.HTTP_201_CREATED)
def post_feedback(
    feedback_in: schemas.SystemFeedbackCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    # Optional dependency: try to get user if token exists, else treat as guest
    token: Optional[str] = Depends(oauth2_scheme)
):
    """
    Public API to submit feedback.
    Supports both registered users (via token) and guests (via guest_email).
    """
    user_id = None
    if token:
        token_data = decode_token(token)
        if token_data:
            user_id = token_data.user_id
    
    # If not registered and no guest_email, raise error
    if not user_id and not feedback_in.guest_email:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest email required for non-authenticated users"
        )
            
    db_feedback = crud_admin.create_feedback(db, feedback_in, user_id=user_id)
    
    # If guest, trigger background task log
    if not user_id:
        background_tasks.add_task(log_feedback_email, feedback_in.guest_email, feedback_in.subject)
        
    return db_feedback
