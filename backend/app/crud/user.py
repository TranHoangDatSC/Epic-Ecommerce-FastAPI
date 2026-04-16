from app import models
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.crud.base import CRUDBase
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password
from app.core.utils import generate_unique_key
from sqlalchemy.orm import joinedload

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """User CRUD operations"""

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """Create user with hashed password (caller must handle commit)"""
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=hash_password(obj_in.password),
            full_name=obj_in.full_name,
            phone_number=obj_in.phone_number,
            address=obj_in.address,
            avatar_url = f"/media/users/user_{obj_in.role_id or 3}_{obj_in.username}.png",
            random_key=generate_unique_key('user'),
        )   
        db.add(db_obj)
        db.flush()  # Get user_id without committing

        # Add role to user_role table
        from app.models import UserRole
        db_user_role = UserRole(user_id=db_obj.user_id, role_id=obj_in.role_id or 3)
        db.add(db_user_role)
        db.flush()

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

    def get_active_users_with_roles(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users with their roles pre-loaded"""
        return (
            db.query(User)
            .options(joinedload(User.user_roles).joinedload(models.UserRole.role)) # Load cả bảng UserRole và Role
            .filter(User.is_deleted == False)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def change_password(self, db: Session, db_user: User, current_password: str, new_password: str) -> bool:
        """Change user's password after verifying current password.

        Returns True on success, False if current password is incorrect.
        """
        # Verify current password
        if not verify_password(current_password, db_user.password_hash):
            return False

        # Set new hashed password
        db_user.password_hash = hash_password(new_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return True
        
    # def update_user(db: Session, db_user: User, user_in: UserUpdate):
    #     update_data = user_in.dict(exclude_unset=True)
    #     for field, value in update_data.items():
    #         setattr(db_user, field, value)
        
    #     db.add(db_user)
    #     db.commit()
    #     db.refresh(db_user)
    #     return db_user

# Create CRUD instance
crud_user = CRUDUser(User)
