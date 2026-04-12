from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models import User, Order, Product, SystemFeedback
from app.schemas import AdminDashboardStats, SystemFeedbackResponse
from typing import List, Optional
from app.models import User, Role, UserRole
from app.core.security import hash_password
from app.core.utils import generate_unique_key
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

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
    # 1. Tách role_id ra để không nhét vào User model
    target_role_id = moderator_data.pop('role_id', 2)
    
    # 2. Tạo User model thuần túy (không dính dáng tới role_id)
    # Lưu ý: Các field password_hash, random_key, is_active là bắt buộc theo model của bạn
    new_user = User(
        username=moderator_data['username'],
        email=moderator_data['email'],
        password_hash=hash_password(moderator_data['password']),
        random_key=generate_unique_key('moderator'),
        full_name=moderator_data['full_name'],
        phone_number=moderator_data.get('phone_number'),
        address=moderator_data.get('address'),
        is_active=True,
        is_deleted=False
    )
    
    try:
        db.add(new_user)
        db.flush() # Để lấy user_id ngay lập tức cho new_user
        
        # 3. Gán Role qua bảng trung gian (Many-to-Many)
        role = db.query(Role).filter(Role.role_id == target_role_id).first()
        if not role:
            raise ValueError(f"Role ID {target_role_id} không tồn tại trong hệ thống")
            
        # Dùng quan hệ roles đã định nghĩa trong models.py
        new_user.roles.append(role) 
        
        db.commit()
        db.refresh(new_user)
        return new_user
        
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Dữ liệu bị trùng (username hoặc email): {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Lỗi database: {str(e)}")

def update_moderator_status(db: Session, moderator_id: int, status: int) -> Optional[User]:
    """Update moderator status (Activate/Deactivate)"""
    db_user = db.query(User).filter(User.user_id == moderator_id).first()
    if db_user:
        db_user.is_active = (status == 1)
        db.commit()
        db.refresh(db_user)
    return db_user