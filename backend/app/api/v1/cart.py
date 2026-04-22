from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Product
from app.schemas import ShoppingCartResponse, ShoppingCartItemCreate, ShoppingCartItemResponse
from app.core.dependencies import check_user_role
from app.crud.shopping_cart import crud_cart
from app.crud.product import crud_product

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=ShoppingCartResponse)
async def get_cart(
    current_user: User = Depends(check_user_role([1, 2, 3])),
    db: Session = Depends(get_db)
) -> ShoppingCartResponse:
    """Get user's shopping cart"""
    cart = crud_cart.get_or_create_by_user_id(db, current_user.user_id)
    return cart


@router.post("/items", response_model=ShoppingCartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_cart_item(
    item_in: ShoppingCartItemCreate,
    current_user: User = Depends(check_user_role([1, 2, 3])),
    db: Session = Depends(get_db)
) -> ShoppingCartItemResponse:
    product = crud_product.get_by_id(db, item_in.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if product.seller_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add your own product to cart"
        )

    if item_in.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Quantity must be greater than zero"
        )

    try:
        cart_item = crud_cart.add_or_update_item(db, current_user.user_id, item_in.product_id, item_in.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return cart_item


@router.put("/items/{cart_item_id}", response_model=ShoppingCartItemResponse)
async def update_cart_item(
    cart_item_id: int,
    item_in: ShoppingCartItemCreate,
    current_user: User = Depends(check_user_role([1, 2, 3])),
    db: Session = Depends(get_db)
) -> ShoppingCartItemResponse:
    existing_item = crud_cart.get_item_by_id(db, cart_item_id)
    if not existing_item or existing_item.cart.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    if item_in.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quantity must be greater than zero")

    try:
        updated_item = crud_cart.update_item_quantity(db, cart_item_id, item_in.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if not updated_item:
        # Item was deleted (quantity <= 0 handled in crud) - though we handle quantity <= 0 above
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    return updated_item


@router.delete("/items/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cart_item(
    cart_item_id: int,
    current_user: User = Depends(check_user_role([1, 2, 3])),
    db: Session = Depends(get_db)
) -> None:
    existing_item = crud_cart.get_item_by_id(db, cart_item_id)
    if not existing_item or existing_item.cart.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    crud_cart.remove_item(db, cart_item_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: User = Depends(check_user_role([1, 2, 3])),
    db: Session = Depends(get_db)
) -> None:
    crud_cart.clear_cart(db, current_user.user_id)