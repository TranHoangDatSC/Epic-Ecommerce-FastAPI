from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.crud.base import CRUDBase
from app.models import Product, Review
from app.schemas import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """Product CRUD operations"""

    def get_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return (
            db.query(Product)
            .options(joinedload(Product.product_images))
            .options(joinedload(Product.reviews).joinedload(Review.reviewer))
            .options(joinedload(Product.seller))
            .filter(Product.product_id == product_id)
            .filter(Product.is_deleted == False)
            .first()
        )

    def get_by_seller(
        self,
        db: Session,
        seller_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get all products by seller"""
        return (
            db.query(Product)
            .filter(Product.seller_id == seller_id)
            .filter(Product.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self,
        db: Session,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
        approved_only: bool = True
    ) -> List[Product]:
        """Get products by category"""
        query = (
            db.query(Product)
            .options(joinedload(Product.product_images))
            .filter(Product.category_id == category_id)
            .filter(Product.is_deleted == False)
        )
        
        if approved_only:
            query = query.filter(Product.status == 1)  # Approved
        
        return query.offset(skip).limit(limit).all()

    def get_approved_products(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at"
    ) -> List[Product]:
        """Get all approved products"""
        query = (
            db.query(Product)
            .options(joinedload(Product.product_images))
            .options(joinedload(Product.seller))
            .filter(Product.status == 1)  # Approved
            .filter(Product.is_deleted == False)
        )
        
        if order_by == "created_at":
            query = query.order_by(Product.created_at.desc())
        elif order_by == "price":
            query = query.order_by(Product.price)
        elif order_by == "rating":
            query = query.order_by(Product.view_count.desc())
        
        return query.offset(skip).limit(limit).all()

    def search_products(
        self,
        db: Session,
        query_str: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Search products by title or description"""
        return (
            db.query(Product)
            .options(joinedload(Product.product_images))
            .options(joinedload(Product.seller))
            .filter(Product.is_deleted == False)
            .filter(Product.status == 1)  # Only approved
            .filter(
                (Product.title.ilike(f"%{query_str}%")) |
                (Product.description.ilike(f"%{query_str}%"))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def increment_view_count(self, db: Session, product_id: int) -> Optional[Product]:
        """Increment product view count"""
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if product:
            product.view_count += 1
            db.add(product)
            db.commit()
            db.refresh(product)
        return product

    def update_product_status(
        self,
        db: Session,
        product_id: int,
        status: int,
        reject_reason: Optional[str] = None,
        approved_by: Optional[int] = None
    ) -> Optional[Product]:
        """Update product status (for admin/moderator approval)"""
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if product:
            product.status = status
            if reject_reason:
                product.reject_reason = reject_reason
            if approved_by:
                product.approved_by = approved_by
            db.add(product)
            db.commit()
            db.refresh(product)
        return product


# Create CRUD instance
crud_product = CRUDProduct(Product)
