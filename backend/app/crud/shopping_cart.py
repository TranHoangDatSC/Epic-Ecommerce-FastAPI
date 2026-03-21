from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models import ShoppingCart, ShoppingCartItem, Product


class CRUDShoppingCart:
    """Shopping cart CRUD operations"""

    def get_by_user_id(self, db: Session, user_id: int) -> ShoppingCart | None:
        return (
            db.query(ShoppingCart)
            .options(
                joinedload(ShoppingCart.cart_items).joinedload(ShoppingCartItem.product)
            )
            .filter(ShoppingCart.user_id == user_id)
            .first()
        )

    def create_cart(self, db: Session, user_id: int) -> ShoppingCart:
        cart = ShoppingCart(user_id=user_id, last_updated=datetime.utcnow())
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart

    def get_or_create_by_user_id(self, db: Session, user_id: int) -> ShoppingCart:
        cart = self.get_by_user_id(db, user_id)
        return cart or self.create_cart(db, user_id)

    def get_item_by_id(self, db: Session, cart_item_id: int) -> ShoppingCartItem | None:
        return db.query(ShoppingCartItem).filter(ShoppingCartItem.cart_item_id == cart_item_id).first()

    def get_item_by_cart_and_product(self, db: Session, cart_id: int, product_id: int) -> ShoppingCartItem | None:
        return (
            db.query(ShoppingCartItem)
            .filter(ShoppingCartItem.cart_id == cart_id)
            .filter(ShoppingCartItem.product_id == product_id)
            .first()
        )

    def add_or_update_item(
        self,
        db: Session,
        user_id: int,
        product_id: int,
        quantity: int
    ) -> ShoppingCartItem:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        cart = self.get_or_create_by_user_id(db, user_id)

        item = self.get_item_by_cart_and_product(db, cart.cart_id, product_id)
        if item:
            item.quantity += quantity
        else:
            existing = db.query(Product).filter(
                Product.product_id == product_id,
                Product.is_deleted == False,
                Product.status == 1
            ).first()
            if not existing:
                raise ValueError("Product not found or not available")

            item = ShoppingCartItem(cart_id=cart.cart_id, product_id=product_id, quantity=quantity)
            db.add(item)

        cart.last_updated = datetime.utcnow()
        db.add(cart)
        db.add(item)
        db.commit()
        db.refresh(item)
        db.refresh(cart)
        return item

    def update_item_quantity(
        self,
        db: Session,
        cart_item_id: int,
        quantity: int
    ) -> ShoppingCartItem | None:
        item = self.get_item_by_id(db, cart_item_id)
        if not item:
            return None
        if quantity <= 0:
            db.delete(item)
            db.commit()
            return None

        item.quantity = quantity
        item.added_at = datetime.utcnow()
        item.cart.last_updated = datetime.utcnow()

        db.add(item)
        db.add(item.cart)
        db.commit()
        db.refresh(item)
        return item

    def remove_item(self, db: Session, cart_item_id: int) -> bool:
        item = self.get_item_by_id(db, cart_item_id)
        if not item:
            return False

        cart = item.cart
        db.delete(item)
        if cart:
            cart.last_updated = datetime.utcnow()
            db.add(cart)

        db.commit()
        return True

    def clear_cart(self, db: Session, user_id: int) -> bool:
        cart = self.get_by_user_id(db, user_id)
        if not cart:
            return False

        db.query(ShoppingCartItem).filter(ShoppingCartItem.cart_id == cart.cart_id).delete()
        cart.last_updated = datetime.utcnow()
        db.add(cart)
        db.commit()
        return True


crud_cart = CRUDShoppingCart()
