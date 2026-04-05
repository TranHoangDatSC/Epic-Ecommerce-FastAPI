from sqlalchemy.orm import Session
from sqlalchemy import func, or_
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

def create_moderator(db: Session, moderator_data: dict, admin_id: int) -> User:
    """Create a new moderator user"""
    from app.core.security import get_password_hash
    from app.models import UserRole
    from app.core.utils import generate_random_key

    # Check if username or email already exists
    existing_user = db.query(User).filter(
        or_(User.username == moderator_data['username'], User.email == moderator_data['email'])
    ).first()

    if existing_user:
        if existing_user.username == moderator_data['username']:
            raise ValueError("Username already exists")
        else:
            raise ValueError("Email already exists")

    # Create new user with moderator role
    hashed_password = get_password_hash(moderator_data['password'])
    new_user = User(
        username=moderator_data['username'],
        email=moderator_data['email'],
        password_hash=hashed_password,
        random_key=generate_random_key(),
        full_name=moderator_data['full_name'],
        phone_number=moderator_data.get('phone_number'),
        address=moderator_data.get('address'),
        is_active=True,
        role_id=2  # Moderator role
    )

    db.add(new_user)
    db.flush()  # Get user_id without committing

    # Add moderator role to user_roles table
    user_role = UserRole(user_id=new_user.user_id, role_id=2)
    db.add(user_role)

    db.commit()
    db.refresh(new_user)
    return new_user

