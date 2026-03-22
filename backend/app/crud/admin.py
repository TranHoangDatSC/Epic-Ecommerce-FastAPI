from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User, Order, Product, SystemFeedback
from app.schemas import AdminDashboardStats, SystemFeedbackResponse
from typing import List, Optional

def get_admin_stats(db: Session) -> AdminDashboardStats:
    """Get statistics for admin dashboard"""
    total_users = db.query(func.count(User.user_id)).filter(User.is_active == True, User.is_deleted == False).scalar()
    total_orders = db.query(func.count(Order.order_id)).filter(Order.is_deleted == False).scalar()
    pending_products = db.query(func.count(Product.product_id)).filter(Product.status == 0, Product.is_deleted == False).scalar()
    
    # Assuming order_status 3 is Delivered/Successful
    total_revenue = db.query(func.sum(Order.final_amount)).filter(Order.order_status == 3, Order.is_deleted == False).scalar() or 0
    
    return AdminDashboardStats(
        total_users=total_users,
        total_orders=total_orders,
        pending_products=pending_products,
        total_revenue=total_revenue
    )

def get_feedbacks(db: Session, skip: int = 0, limit: int = 100) -> List[SystemFeedback]:
    """Get all system feedbacks, ordered by creation date descending"""
    return db.query(SystemFeedback).order_by(SystemFeedback.created_at.desc()).offset(skip).limit(limit).all()

def update_feedback_status(db: Session, feedback_id: int, status: int) -> Optional[SystemFeedback]:
    """Update feedback status"""
    db_feedback = db.query(SystemFeedback).filter(SystemFeedback.feedback_id == feedback_id).first()
    if db_feedback:
        db_feedback.status = status
        db.commit()
        db.refresh(db_feedback)
    return db_feedback

def get_users_list(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    """Get list of users with pagination"""
    return db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()

def create_feedback(db: Session, feedback_in: SystemFeedbackResponse, user_id: Optional[int] = None) -> SystemFeedback:
    """Create a new system feedback/contact message"""
    # Note: feedback_in is SystemFeedbackCreate in reality, but we use dict() anyway
    db_feedback = SystemFeedback(
        user_id=user_id,
        guest_email=getattr(feedback_in, 'guest_email', None),
        subject=feedback_in.subject,
        content=feedback_in.content,
        status=0
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

