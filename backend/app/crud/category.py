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


# Create CRUD instance
crud_category = CRUDCategory(Category)
