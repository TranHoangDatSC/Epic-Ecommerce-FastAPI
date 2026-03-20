from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Category
from app.schemas import CategoryResponse, CategoryCreate, CategoryUpdate
from app.core.dependencies import get_current_user, check_admin, check_moderator
from app.crud.category import crud_category

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
) -> list[CategoryResponse]:
    """
    List all categories.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **active_only**: Filter by active status
    """
    query = db.query(Category).filter(Category.is_deleted == False)
    
    if active_only:
        query = query.filter(Category.is_active == True)
    
    categories = query.offset(skip).limit(limit).all()
    return categories


@router.get("/parent", response_model=list[CategoryResponse])
async def list_parent_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> list[CategoryResponse]:
    """List parent categories (categories without parent)"""
    categories = crud_category.get_parent_categories(db, skip=skip, limit=limit)
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
) -> CategoryResponse:
    """Get category by ID"""
    category = crud_category.get_by_id(db, category_id=category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.get("/{category_id}/children", response_model=list[CategoryResponse])
async def get_category_children(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> list[CategoryResponse]:
    """Get child categories"""
    # Check parent category exists
    parent = crud_category.get_by_id(db, category_id=category_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent category not found"
        )
    
    children = crud_category.get_child_categories(
        db,
        parent_id=category_id,
        skip=skip,
        limit=limit
    )
    return children


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    admin_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
) -> CategoryResponse:
    """
    Create a new category (Admin only).
    
    Requires admin role.
    """
    # Check if name already exists
    existing = crud_category.get_by_name(db, name=category_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )
    
    # Validate parent category if provided
    if category_in.parent_id:
        parent = crud_category.get_by_id(db, category_id=category_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )
    
    category = crud_category.create(db=db, obj_in=category_in)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    admin_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
) -> CategoryResponse:
    """
    Update a category (Admin only).
    
    Requires admin role.
    """
    category = crud_category.get_by_id(db, category_id=category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if new name already exists (if name is being updated)
    if category_update.name and category_update.name != category.name:
        existing = crud_category.get_by_name(db, name=category_update.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )
    
    # Validate parent category if being updated
    if category_update.parent_id and category_update.parent_id != category.parent_id:
        parent = crud_category.get_by_id(db, category_id=category_update.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )
    
    updated_category = crud_category.update(db=db, db_obj=category, obj_in=category_update)
    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    admin_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a category (Admin only).
    
    Soft deletes the category.
    """
    category = crud_category.get_by_id(db, category_id=category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category.is_deleted = True
    db.add(category)
    db.commit()
