from sqlalchemy.orm import Session
from typing import Optional, List
from app.crud.base import CRUDBase
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    """Category CRUD operations"""

    def get_by_id(self, db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return (
            db.query(Category)
            .filter(Category.category_id == category_id)
            .filter(Category.is_deleted == False)
            .first()
        )

    def get_by_name(self, db: Session, name: str) -> Optional[Category]:
        """Get category by name"""
        return (
            db.query(Category)
            .filter(Category.name == name)
            .filter(Category.is_deleted == False)
            .first()
        )

    def get_active_categories(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """Get all active categories"""
        return (
            db.query(Category)
            .filter(Category.is_active == True)
            .filter(Category.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_parent_categories(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """Get parent categories (no parent_id)"""
        return (
            db.query(Category)
            .filter(Category.parent_id == None)
            .filter(Category.is_active == True)
            .filter(Category.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_child_categories(
        self,
        db: Session,
        parent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """Get child categories by parent"""
        return (
            db.query(Category)
            .filter(Category.parent_id == parent_id)
            .filter(Category.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def has_products(self, db: Session, category_id: int) -> bool:
        """Check if category has any products attached"""
        from app.models import Product
        count = db.query(Product).filter(Product.category_id == category_id).count()
        return count > 0

    def get_by_id_with_deleted(self, db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID including soft-deleted ones"""
        return (
            db.query(Category)
            .filter(Category.category_id == category_id)
            .first()
        )
    def soft_delete_category_and_products(self, db: Session, category_id: int):
        category = self.get_by_id(db, category_id)
        if category:
            category.is_deleted = True
            from app.models import Product
            products = db.query(Product).filter(Product.category_id == category_id).all()
            for p in products:
                p.status = 0  
            db.commit()

    def hard_delete(self, db: Session, category_id: int) -> bool:
        """Permanently delete a category from DB"""
        db_obj = self.get_by_id_with_deleted(db, category_id)
        if not db_obj:
            return False
        
        db.delete(db_obj)
        db.commit()
        return True


# Create CRUD instance
crud_category = CRUDCategory(Category)
