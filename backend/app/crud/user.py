from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.crud.base import CRUDBase
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.core.security import hash_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """User CRUD operations"""

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """Create user with hashed password"""
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=hash_password(obj_in.password),
            full_name=obj_in.full_name,
            phone_number=obj_in.phone_number,
            address=obj_in.address,
            random_key=obj_in.username,  # Could be replaced with actual random key generation
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_active_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get all active users"""
        return (
            db.query(User)
            .filter(User.is_deleted == False)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.user_id == user_id).first()


# Create CRUD instance
crud_user = CRUDUser(User)
