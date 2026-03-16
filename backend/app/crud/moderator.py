from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models, schemas
from app.crud.base import CRUDBase
from app.core.exceptions import NotFoundException, ValidationException
from typing import List, Optional


class CRUDModerator(CRUDBase[models.Product, schemas.ProductApprovalRequest, schemas.ProductApprovalRequest]):
    """CRUD operations for moderator functions"""

    def approve_product(
        self, db: Session, *, product_id: int, status: int, reject_reason: Optional[str] = None, moderator_id: int
    ) -> models.Product:
        """Approve or reject a product"""
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
        """Get all pending products for approval"""
        return db.query(models.Product).filter(
            and_(models.Product.status == 0, models.Product.is_deleted == False)
        ).all()

    def handle_violation_report(self, db: Session, *, review_id: int, moderator_id: int) -> models.Review:
        """Handle violation report for a review"""
        review = db.query(models.Review).filter(
            and_(models.Review.review_id == review_id, models.Review.is_deleted == False)
        ).first()

        if not review:
            raise NotFoundException("Review not found")

        # Get the product and seller
        product = review.product
        seller = product.seller

        # Check if seller has role_id = 3
        has_seller_role = db.query(models.UserRole).filter(
            and_(models.UserRole.user_id == seller.user_id, models.UserRole.role_id == 3)
        ).first() is not None

        # Deactivate the product
        product.status = 2  # Rejected
        product.reject_reason = f"Violation reported on review {review_id}"

        # Decrease seller's trust score only if they have seller role
        if has_seller_role:
            current_score = seller.trust_score if seller.trust_score is not None else 0.0
            seller.trust_score = max(0.0, current_score - 10.0)

            # Log the violation
            violation_log = models.ViolationLog(
                user_id=seller.user_id,
                reason=f"Violation on review {review_id} for product {product.product_id}",
                action_taken="PRODUCT_REMOVAL"
            )
            db.add(violation_log)

            # If trust score <= 0, ban the user
            if seller.trust_score <= 0:
                seller.is_active = False
                ban_log = models.ViolationLog(
                    user_id=seller.user_id,
                    reason="Trust score dropped to 0 or below",
                    action_taken="BAN"
                )
                db.add(ban_log)
        else:
            # Log without trust score penalty
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
        """Get reviews that are potential violations (1 star or reported)"""
        return db.query(models.Review).filter(
            and_(models.Review.rating == 1, models.Review.is_deleted == False)
        ).all()

    def toggle_user_status(
        self,
        db: Session,
        *,
        user_id: int,
        is_active: bool,
        reason: str,
        moderator_id: int
    ) -> models.User:
        """Activate/deactivate a user account (only for role_id=3 users)."""
        user = db.query(models.User).filter(
            and_(models.User.user_id == user_id, models.User.is_deleted == False)
        ).first()

        if not user:
            raise NotFoundException("User not found")

        # Only allow changing status for users with role_id=3 (User role)
        if not any(ur.role_id == 3 for ur in user.user_roles):
            raise ValidationException("Can only change status for users with User role (role_id=3)")

        # If no state change, do nothing (idempotent)
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

    def get_violation_logs(self, db: Session, *, user_id: Optional[int] = None) -> List[models.ViolationLog]:
        """Get violation logs, optionally filtered by user"""
        query = db.query(models.ViolationLog)
        if user_id:
            query = query.filter(models.ViolationLog.user_id == user_id)
        return query.order_by(models.ViolationLog.created_at.desc()).all()


moderator = CRUDModerator(models.Product)