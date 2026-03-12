from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Order, Product, ContactInfo
from app.schemas import OrderResponse, OrderDetailResponse_Extended, OrderCreate, OrderUpdate
from app.core.dependencies import get_current_user, check_admin
from app.crud.order import crud_order
from decimal import Decimal

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[OrderResponse]:
    """
    Get current user's orders.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **status_filter**: Filter by order status (0-4)
    """
    if status_filter is not None:
        orders = (
            db.query(Order)
            .filter(Order.buyer_id == current_user.user_id)
            .filter(Order.is_deleted == False)
            .filter(Order.order_status == status_filter)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        orders = crud_order.get_by_buyer(
            db,
            buyer_id=current_user.user_id,
            skip=skip,
            limit=limit
        )
    
    return orders


@router.get("/{order_id}", response_model=OrderDetailResponse_Extended)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrderDetailResponse_Extended:
    """
    Get order details.
    
    User can only view their own orders. Admin can view any order.
    """
    order = crud_order.get_by_id(db, order_id=order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permission
    user_roles = [role.role_id for role in current_user.user_roles]
    is_admin = 1 in user_roles
    
    if not (is_admin or order.buyer_id == current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own orders"
        )
    
    return order


@router.post("", response_model=OrderDetailResponse_Extended, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrderDetailResponse_Extended:
    """
    Create a new order.
    
    **Important**: User cannot order their own products.
    
    - **contact_id**: Delivery contact info ID
    - **payment_method_id**: Payment method ID
    - **order_items**: List of products with quantities
    - **voucher_id**: Optional voucher code ID
    - **shipping_fee**: Shipping fee amount
    - **notes**: Optional order notes
    """
    # Validate contact info exists and belongs to current user
    contact = db.query(ContactInfo).filter(
        ContactInfo.contact_id == order_in.contact_id,
        ContactInfo.user_id == current_user.user_id,
        ContactInfo.is_deleted == False
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contact information"
        )
    
    # Validate products and check user is not seller
    all_product_ids = set()
    for item in order_in.order_items:
        product = db.query(Product).filter(
            Product.product_id == item.product_id,
            Product.is_deleted == False,
            Product.status == 1  # Only approved products
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item.product_id} not found or not available"
            )
        
        # **KEY VALIDATION**: User cannot buy their own products
        if product.seller_id == current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You cannot order product '{product.title}' because you are the seller"
            )
        
        # Check quantity availability
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.title}' has insufficient quantity. Available: {product.quantity}, Requested: {item.quantity}"
            )
        
        all_product_ids.add(item.product_id)
    
    # Create order with items
    order = crud_order.create_order(
        db=db,
        buyer_id=current_user.user_id,
        contact_id=order_in.contact_id,
        payment_method_id=order_in.payment_method_id,
        order_items=[item.dict() for item in order_in.order_items],
        shipping_fee=order_in.shipping_fee,
        discount_amount=Decimal("0"),  # Will be calculated based on voucher later
        voucher_id=order_in.voucher_id,
        notes=order_in.notes
    )
    
    # Update product quantities
    for item in order_in.order_items:
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        if product:
            product.quantity -= item.quantity
            db.add(product)
    
    db.commit()
    db.refresh(order)
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrderResponse:
    """
    Update an order.
    
    - Regular users can only cancel pending orders
    - Moderators and admins can update status and tracking number
    """
    order = crud_order.get_by_id(db, order_id=order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permission
    user_roles = [role.role_id for role in current_user.user_roles]
    is_admin = 1 in user_roles
    is_moderator = 2 in user_roles or is_admin
    is_owner = order.buyer_id == current_user.user_id
    
    # Regular users can only cancel their pending orders
    if not (is_moderator or is_admin):
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own orders"
            )
        
        # User can only cancel pending orders
        if order_update.order_status is not None:
            if order_update.order_status == 4:  # Cancel
                if order.order_status != 0:  # Not pending
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Can only cancel pending orders"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Regular users can only cancel orders"
                )
    
    updated_order = crud_order.update_order_status(
        db=db,
        order_id=order_id,
        new_status=order_update.order_status or order.order_status,
        tracking_number=order_update.tracking_number
    )
    
    if order_update.notes:
        updated_order.notes = order_update.notes
        db.add(updated_order)
        db.commit()
    
    return updated_order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    admin_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete an order (Admin only).
    
    Soft deletes the order.
    """
    order = crud_order.get_by_id(db, order_id=order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.is_deleted = True
    db.add(order)
    db.commit()


# ==================== Admin endpoints ====================

@router.get("/admin/all", response_model=list[OrderResponse])
async def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: int = Query(None),
    admin_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
) -> list[OrderResponse]:
    """
    Get all orders (Admin only).
    
    - **status_filter**: Filter by order status (0-4)
    """
    query = db.query(Order).filter(Order.is_deleted == False)
    
    if status_filter is not None:
        query = query.filter(Order.order_status == status_filter)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/admin/pending", response_model=list[OrderResponse])
async def get_pending_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
) -> list[OrderResponse]:
    """Get all pending orders (Admin only)"""
    orders = crud_order.get_pending_orders(db, skip=skip, limit=limit)
    return orders
