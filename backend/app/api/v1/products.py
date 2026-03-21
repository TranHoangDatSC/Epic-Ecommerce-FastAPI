from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Product, ProductImage
from app.schemas import ProductResponse, ProductDetailResponse, ProductCreate, ProductUpdate
from app.core.dependencies import check_admin, check_moderator, check_user_role, get_current_user_optional
from app.crud.product import crud_product
from app.crud.category import crud_category
import os
from pathlib import Path

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: int = Query(None),
    search: str = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|price|rating)$"),
    current_user: User = Depends(get_current_user_optional),
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

    # Nếu user đã đăng nhập, không hiển thị sản phẩm do chính họ bán
    if current_user:
        products = [p for p in products if p.seller_id != current_user.user_id]

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
    files: List[UploadFile] = File(...),
    category_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    quantity: int = Form(...),
    video_url: str = Form(None),
    weight_grams: int = Form(None),
    dimensions: str = Form(None),
    condition_rating: int = Form(None),
    warranty_months: int = Form(0),
    transfer_method: int = Form(1),
    current_user: User = Depends(check_user_role([3])),
    db: Session = Depends(get_db)
) -> ProductResponse:
    """
    Create a new product with images.
    
    Requires authentication. Status will be 0 (pending for review).
    At least one image file is required.
    """
    # Validate at least one image
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one image file is required"
        )

    # Verify category exists
    category = crud_category.get_by_id(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )

    # Create product data
    product_data = {
        'seller_id': current_user.user_id,
        'category_id': category_id,
        'title': title,
        'description': description,
        'price': price,
        'quantity': quantity,
        'video_url': video_url,
        'weight_grams': weight_grams,
        'dimensions': dimensions,
        'condition_rating': condition_rating,
        'warranty_months': warranty_months,
        'transfer_method': transfer_method,
        'status': 0  # Pending
    }

    # Start transaction
    try:
        # Create product
        product = Product(**product_data)
        db.add(product)
        db.flush()  # Get product_id without committing

        # Get media directory
        media_dir = Path(__file__).parent.parent.parent.parent / "media" / "products"
        media_dir.mkdir(parents=True, exist_ok=True)

        # Get current image count for this product
        existing_images_count = db.query(ProductImage).filter(ProductImage.product_id == product.product_id).count()

        # Process and save images
        for i, file in enumerate(files, start=existing_images_count + 1):
            # Validate file type
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} is not an image"
                )

            # Generate new filename
            original_name = Path(file.filename).stem
            extension = Path(file.filename).suffix.lower()
            new_filename = f"prod_{product.product_id}_{i}_{original_name}{extension}"
            file_path = media_dir / new_filename

            # Read file content
            content = await file.read()

            # Save file
            with open(file_path, "wb") as f:
                f.write(content)

            # Create database record
            image_url = f"/media/products/{new_filename}"
            is_primary = (i == 1)  # First image is primary

            product_image = ProductImage(
                product_id=product.product_id,
                image_url=image_url,
                alt_text=f"{title} - Image {i}",
                is_primary=is_primary,
                display_order=i
            )
            db.add(product_image)

        # Commit transaction
        db.commit()
        db.refresh(product)

        return product

    except Exception as e:
        db.rollback()
        # Clean up uploaded files if any
        media_dir = Path(__file__).parent.parent.parent.parent / "media" / "products"
        for file in files:
            if hasattr(file, 'filename'):
                original_name = Path(file.filename).stem
                extension = Path(file.filename).suffix.lower()
                for i in range(1, len(files) + 1):
                    new_filename = f"prod_{product.product_id}_{i}_{original_name}{extension}"
                    file_path = media_dir / new_filename
                    if file_path.exists():
                        file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


@router.get("/seller/my-products", response_model=list[ProductResponse])
async def get_my_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(check_user_role([1, 2, 3])),
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
    current_user: User = Depends(check_user_role([1, 2, 3])),
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
    current_user: User = Depends(check_user_role([1, 2, 3])),
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
