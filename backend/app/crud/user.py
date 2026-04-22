import random
from datetime import datetime
from datetime import timedelta
from pydantic_settings.sources.providers import secrets
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
from secrets import token_urlsafe

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """User CRUD operations"""

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """Create user, assign role, and auto-create default contact info"""
        from app.models import UserRole, ContactInfo
        
        # 1. Tạo đối tượng User
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=hash_password(obj_in.password),
            full_name=obj_in.full_name,
            phone_number=obj_in.phone_number,
            address=obj_in.address,
            avatar_url=f"/media/users/user_{obj_in.role_id or 3}_{obj_in.username}.png",
            random_key=generate_unique_key('user'),
        )
        db.add(db_obj)
        db.flush()  # Đẩy dữ liệu xuống để lấy db_obj.user_id

        # 2. Gán Role cho User
        db_user_role = UserRole(user_id=db_obj.user_id, role_id=obj_in.role_id or 3)
        db.add(db_user_role)

        # 3. TỰ ĐỘNG MAPPING SANG CONTACT INFO
        # Lấy thông tin từ User vừa điền để làm địa chỉ mặc định
        
        db_contact = ContactInfo(
            user_id=db_obj.user_id,
            full_name=obj_in.full_name,
            phone_number=obj_in.phone_number,
            address=obj_in.address,
            # Bạn có thể để trống hoặc mặc định các trường tỉnh/thành nếu UserCreate không có
            province=None, 
            district=None,
            ward=None,
            is_default=True,
            is_deleted=False
        )
        db.add(db_contact)

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
    
    def request_password_reset(self, db: Session, email: str) -> Optional[str]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        
        # Dùng hàm đã import ở trên
        token = token_urlsafe(32) 
        
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
        return token

    def reset_password(self, db: Session, token: str, new_password: str) -> bool:
        user = db.query(User).filter(User.password_reset_token == token).first()
        if not user or not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
            return False
        user.password_hash = hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        db.commit()
        return True
        
    def request_otp_reset(self, db: Session, email: str) -> Optional[str]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        
        # Tạo mã OTP 6 số
        otp = f"{random.randint(100000, 999999)}"
        user.otp_code = otp
        user.otp_expires = datetime.utcnow() + timedelta(minutes=5) # OTP chỉ có hiệu lực 5 phút
        db.commit()
        return otp # Gửi cái này qua email

    # Trong crud/user.py

    def request_otp_reset(self, db: Session, email: str) -> Optional[str]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        
        otp = f"{random.randint(100000, 999999)}"
        
        # Gán vào trường CÓ SẴN trong model thay vì trường "ma"
        user.password_reset_token = otp 
        user.password_reset_expires = datetime.utcnow() + timedelta(minutes=5)
        
        db.commit()
        return otp

    def verify_otp_and_reset(self, db: Session, email: str, otp: str, new_password: str) -> bool:
        user = self.get_by_email(db, email=email)
        
        # Dùng password_reset_token làm nơi chứa OTP (tránh lỗi attribute)
        if not user or user.password_reset_token != otp or \
        not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
            return False
        
        user.password_hash = hash_password(new_password)
        
        # Reset lại token và thời hạn
        user.password_reset_token = None
        user.password_reset_expires = None
        
        db.commit()
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
