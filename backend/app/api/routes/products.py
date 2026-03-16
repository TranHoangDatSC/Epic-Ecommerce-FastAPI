from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Product
from app.schemas import ProductResponse, ProductDetailResponse, ProductCreate, ProductUpdate
from app.core.dependencies import get_current_user, check_admin, check_moderator
from app.crud.product import crud_product
from app.crud.category import crud_category

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: int = Query(None),
    search: str = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|price|rating)$"),
    db: Session = Depends(get_db)
) -> list[ProductResponse]:
    """
    List approved products.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **category_id**: Filter by category
    - **search**: Search in title and description
    - **sort_by**: Sort by created_at, price, or rating
    """
    if search:
        products = crud_product.search_products(
            db,
            query_str=search,
            skip=skip,
            limit=limit
        )
    elif category_id:
        products = crud_product.get_by_category(
            db,
            category_id=category_id,
            skip=skip,
            limit=limit,
            approved_only=True
        )
    else:
        products = crud_product.get_approved_products(
            db,
            skip=skip,
            limit=limit,
            order_by=sort_by
        )
    
    return products


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> ProductDetailResponse:
    """Get product details by ID"""
    product = crud_product.get_by_id(db, product_id=product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Increment view count
    crud_product.increment_view_count(db, product_id=product_id)
    
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProductResponse:
    """
    Create a new product.
    
    Requires authentication. Status will be 0 (pending for review).
    """
    # Verify category exists
    category = crud_category.get_by_id(db, category_id=product_in.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )
    
    # Create product with seller_id
    product_data = product_in.dict()
    product_data['seller_id'] = current_user.user_id
    product_data['status'] = 0  # Pending
    
    product = Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product


@router.get("/seller/my-products", response_model=list[ProductResponse])
async def get_my_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[ProductResponse]:
    """Get current user's products"""
    products = crud_product.get_by_seller(
        db,
        seller_id=current_user.user_id,
        skip=skip,
        limit=limit
    )
    return products


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProductResponse:
    """
    Update a product.
    
    Only the seller or admin can update the product.
    """
    product = crud_product.get_by_id(db, product_id=product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check permission (seller or admin)
    user_roles = [role.role_id for role in current_user.user_roles]
    is_admin = 1 in user_roles
    is_seller = product.seller_id == current_user.user_id
    
    if not (is_admin or is_seller):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only seller or admin can update this product"
        )
    
    # If category is being updated, verify it exists
    if product_update.category_id and product_update.category_id != product.category_id:
        category = crud_category.get_by_id(db, category_id=product_update.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
    
    updated_product = crud_product.update(db=db, db_obj=product, obj_in=product_update)
    return updated_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a product.
    
    Only the seller or admin can delete the product.
    """
    product = crud_product.get_by_id(db, product_id=product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check permission
    user_roles = [role.role_id for role in current_user.user_roles]
    is_admin = 1 in user_roles
    is_seller = product.seller_id == current_user.user_id
    
    if not (is_admin or is_seller):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only seller or admin can delete this product"
        )
    
    product.is_deleted = True
    db.add(product)
    db.commit()


# ==================== Moderation endpoints ====================

@router.get("/pending/all", response_model=list[ProductResponse])
async def get_pending_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    moderator: User = Depends(check_moderator),
    db: Session = Depends(get_db)
) -> list[ProductResponse]:
    """
    Get all pending products (Moderator only).
    
    Status 0 = Pending for review.
    """
    products = (
        db.query(Product)
        .filter(Product.status == 0)  # Pending
        .filter(Product.is_deleted == False)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return products


@router.post("/{product_id}/approve", response_model=ProductResponse)
async def approve_product(
    product_id: int,
    moderator: User = Depends(check_moderator),
    db: Session = Depends(get_db)
) -> ProductResponse:
    """
    Approve a product (Moderator only).
    
    Sets status to 1 (Approved).
    """
    product = db.query(Product).filter(Product.product_id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending products can be approved"
        )
    
    product.status = 1  # Approved
    product.approved_by = moderator.user_id
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product


@router.post("/{product_id}/reject", response_model=ProductResponse)
async def reject_product(
    product_id: int,
    reject_reason: str = Query(..., min_length=10),
    moderator: User = Depends(check_moderator),
    db: Session = Depends(get_db)
) -> ProductResponse:
    """
    Reject a product (Moderator only).
    
    Sets status to 2 (Rejected) with reason.
    """
    product = db.query(Product).filter(Product.product_id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending products can be rejected"
        )
    
    product.status = 2  # Rejected
    product.reject_reason = reject_reason
    product.approved_by = moderator.user_id
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product
