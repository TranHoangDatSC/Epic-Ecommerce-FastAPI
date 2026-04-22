from typing import Generic, TypeVar, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import inspect

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base CRUD class with common operations"""

    def __init__(self, model: type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        skip_deleted: bool = True
    ) -> List[ModelType]:
        """Get all records with pagination"""
        query = db.query(self.model)
        
        # Skip deleted records if applicable
        if skip_deleted and hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        obj_data = obj_in.dict(exclude_unset=True)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict
    ) -> ModelType:
        """Update a record"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None and hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        """Soft delete a record (set is_deleted = True)"""
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        
        if db_obj is None:
            return False
        
        if hasattr(db_obj, 'is_deleted'):
            db_obj.is_deleted = True
            db.add(db_obj)
            db.commit()
            return True
        else:
            # Hard delete if model doesn't support soft delete
            db.delete(db_obj)
            db.commit()
            return True

    def hard_delete(self, db: Session, id: int) -> bool:
        """Permanently delete a record"""
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        
        if db_obj is None:
            return False
        
        db.delete(db_obj)
        db.commit()
        return True
