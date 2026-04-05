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
    """Create a new moderator user with comprehensive error handling"""
    from app.core.security import hash_password
    from app.models import UserRole
    from app.core.utils import generate_unique_key
    from sqlalchemy.exc import IntegrityError, SQLAlchemyError
    import traceback

    try:
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if field not in moderator_data or not moderator_data[field]:
                raise ValueError(f"Field '{field}' is required and cannot be empty")

        # Validate field types
        if not isinstance(moderator_data['username'], str):
            raise ValueError("Username must be a string")
        if not isinstance(moderator_data['email'], str):
            raise ValueError("Email must be a string")
        if not isinstance(moderator_data['password'], str):
            raise ValueError("Password must be a string")
        if not isinstance(moderator_data['full_name'], str):
            raise ValueError("Full name must be a string")

        # Validate field lengths
        username = moderator_data['username'].strip()
        email = moderator_data['email'].strip()
        password = moderator_data['password']
        full_name = moderator_data['full_name'].strip()

        if len(username) < 3 or len(username) > 50:
            raise ValueError(f"Username must be between 3 and 50 characters (got {len(username)})")
        if len(email) < 5 or len(email) > 100:
            raise ValueError(f"Email must be between 5 and 100 characters (got {len(email)})")
        if len(password) < 6:
            raise ValueError(f"Password must be at least 6 characters (got {len(password)})")
        if len(full_name) < 1 or len(full_name) > 100:
            raise ValueError(f"Full name must be between 1 and 100 characters (got {len(full_name)})")

        # Validate email format
        if '@' not in email or '.' not in email.split('@')[1]:
            raise ValueError("Invalid email format")

        # Check if username or email already exists
        existing_user = db.query(User).filter(
            or_(User.username == username, User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                raise ValueError(f"Username '{username}' already exists")
            else:
                raise ValueError(f"Email '{email}' already exists")

        # Hash password
        try:
            hashed_password = hash_password(password)
        except Exception as e:
            raise ValueError(f"Error hashing password: {str(e)}")

        # Generate unique key
        try:
            random_key = generate_unique_key('moderator')
        except Exception as e:
            raise ValueError(f"Error generating unique key: {str(e)}")

        # Create new user with moderator role
        try:
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                random_key=random_key,
                full_name=full_name,
                phone_number=moderator_data.get('phone_number', '').strip() or None,
                address=moderator_data.get('address', '').strip() or None,
                is_active=True,
                role_id=2  # Moderator role
            )
            db.add(new_user)
            db.flush()  # Get user_id without committing
        except IntegrityError as e:
            db.rollback()
            if 'username' in str(e).lower():
                raise ValueError(f"Username '{username}' already exists (duplicate key error)")
            elif 'email' in str(e).lower():
                raise ValueError(f"Email '{email}' already exists (duplicate key error)")
            elif 'random_key' in str(e).lower():
                raise ValueError("Random key collision - please try again")
            else:
                raise ValueError(f"Database integrity error: {str(e)}")
        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"Database error while creating user: {str(e)}")

        # Add moderator role to user_roles table
        try:
            user_role = UserRole(user_id=new_user.user_id, role_id=2)
            db.add(user_role)
            db.flush()
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error adding moderator role: {str(e)}")
        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"Database error while adding role: {str(e)}")

        # Commit transaction
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Commit error - integrity violation: {str(e)}")
        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"Commit error: {str(e)}")

        # Refresh user object
        try:
            db.refresh(new_user)
        except Exception as e:
            raise ValueError(f"Error refreshing user data: {str(e)}")

        return new_user

    except ValueError:
        # Re-raise ValueError with clear message
        raise
    except Exception as e:
        # Catch any unexpected errors
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"ERROR in create_moderator (CRUD): {error_msg}")
        traceback.print_exc()
        raise ValueError(f"Unexpected error creating moderator: {error_msg}")

