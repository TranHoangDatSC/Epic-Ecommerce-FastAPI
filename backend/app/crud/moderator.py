from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models, schemas
from app.crud.base import CRUDBase
from app.core.exceptions import NotFoundException, ValidationException
from typing import List, Optional
from sqlalchemy.orm import joinedload
from app.models import User

class CRUDModerator(CRUDBase[models.Product, schemas.ProductApprovalRequest, schemas.ProductApprovalRequest]):
    """CRUD operations for moderator functions"""

    def approve_product(self, db: Session, *, product_id: int, status: int, reject_reason: Optional[str] = None, moderator_id: int) -> models.Product:
        product = db.query(models.Product).filter(
            and_(models.Product.product_id == product_id, models.Product.is_deleted == False)
        ).first()
        if not product:
            raise NotFoundException("Product not found")
        if status not in [0, 1, 2]:
            raise ValidationException("Invalid status value")
        
        product.status = status
        if status == 2:  # Rejected
            if not reject_reason:
                raise ValidationException("Reject reason is required for rejection")
            product.reject_reason = reject_reason
        elif status == 1:  # Approved
            product.approved_by = moderator_id
        
        db.commit()
        db.refresh(product)
        return product

    def get_pending_products(self, db: Session) -> List[models.Product]:
        return db.query(models.Product).filter(
            and_(models.Product.status == 0, models.Product.is_deleted == False)
        ).all()

    def get_users_by_role(self, db: Session, *, role_id: int) -> List[models.User]:
        return db.query(models.User).join(models.UserRole).filter(
            and_(models.UserRole.role_id == role_id, models.User.is_deleted == False)
        ).distinct().all()

    def handle_violation_report(self, db: Session, *, review_id: int, moderator_id: int) -> models.Review:
        review = db.query(models.Review).filter(
            and_(models.Review.review_id == review_id, models.Review.is_deleted == False)
        ).first()
        if not review:
            raise NotFoundException("Review not found")
        
        product = review.product
        seller = product.seller
        
        has_seller_role = db.query(models.UserRole).filter(
            and_(models.UserRole.user_id == seller.user_id, models.UserRole.role_id == 3)
        ).first() is not None

        product.status = 2
        product.reject_reason = f"Violation reported on review {review_id}"

        if has_seller_role:
            current_score = seller.trust_score if seller.trust_score is not None else 0.0
            seller.trust_score = max(0.0, current_score - 10.0)
            
            violation_log = models.ViolationLog(
                user_id=seller.user_id,
                reason=f"Violation on review {review_id} for product {product.product_id}",
                action_taken="PRODUCT_REMOVAL"
            )
            db.add(violation_log)

            if seller.trust_score <= 0:
                seller.is_active = False
                ban_log = models.ViolationLog(
                    user_id=seller.user_id,
                    reason="Trust score dropped to 0 or below",
                    action_taken="BAN"
                )
                db.add(ban_log)
        else:
            violation_log = models.ViolationLog(
                user_id=seller.user_id,
                reason=f"Violation on review {review_id} for product {product.product_id} (no trust score penalty - not a seller)",
                action_taken="PRODUCT_REMOVAL"
            )
            db.add(violation_log)
            
        db.commit()
        db.refresh(review)
        return review

    def get_violation_reviews(self, db: Session) -> List[models.Review]:
        return db.query(models.Review).filter(
            and_(models.Review.rating == 1, models.Review.is_deleted == False)
        ).all()

    def toggle_user_status(self, db: Session, *, user_id: int, is_active: bool, reason: str, moderator_id: int) -> models.User:
        # ĐÃ SỬA: Dùng User.roles thay vì User.user_roles
        user = db.query(User).options(joinedload(User.roles)).filter(User.user_id == user_id).first()
        if not user:
            raise NotFoundException("User not found")

        # ĐÃ SỬA: Dùng user.roles thay vì user.user_roles
        if not any(role.role_id == 3 for role in user.roles):
            raise ValidationException("Can only change status for users with User role (role_id=3)")

        if user.is_active == is_active:
            action = "ACTIVATE" if is_active else "DEACTIVATE"
            raise ValidationException(f"User is already {action.lower()}")
            
        user.is_active = is_active
        action_taken = "ACTIVATE" if is_active else "DEACTIVATE"
        
        violation_log = models.ViolationLog(
            user_id=user_id,
            reason=reason,
            action_taken=action_taken
        )
        db.add(violation_log)
        db.commit()
        db.refresh(user)
        return user

    def get_moderators(self, db: Session, include_deleted: bool = False) -> List[models.User]:
        query = db.query(models.User).join(models.UserRole).filter(models.UserRole.role_id == 2)
        if not include_deleted:
            query = query.filter(models.User.is_deleted == False)
        return query.distinct().all()

    def toggle_moderator_status(self, db: Session, *, user_id: int, is_active: bool, reason: str, admin_id: int) -> models.User:
        user = db.query(models.User).options(joinedload(models.User.roles)).filter(models.User.user_id == user_id).first()
        if not user:
            raise NotFoundException("User not found")
            
        is_moderator = any(role.role_id == 2 for role in user.roles)
        if not is_moderator:
            raise ValidationException("Can only change status for users with Moderator role (role_id=2)")
            
        if user.is_active == is_active:
            action = "ACTIVATE" if is_active else "DEACTIVATE"
            raise ValidationException(f"Moderator is already {action.lower()}")
            
        user.is_active = is_active
        user.is_deleted = not is_active
        
        violation_log = models.ViolationLog(
            user_id=user_id,
            reason=reason,
            action_taken="ACTIVATE_MODERATOR" if is_active else "DEACTIVATE_MODERATOR"
        )
        db.add(violation_log)
        db.commit()
        db.refresh(user)
        return user

moderator = CRUDModerator(models.Product)