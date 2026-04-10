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

        # Use FOR UPDATE to prevent race conditions during stock check
        product = db.query(Product).filter(
            Product.product_id == product_id,
            Product.is_deleted == False,
            Product.status == 1 # Active/Approved
        ).with_for_update().first()

        if not product:
            raise ValueError("Sản phẩm không tồn tại hoặc đã bị xóa")
        
        if product.quantity < quantity:
            raise ValueError(f"Sản phẩm hiện chỉ còn {product.quantity} món. Vui lòng giảm số lượng!")

        cart = self.get_or_create_by_user_id(db, user_id)
        item = self.get_item_by_cart_and_product(db, cart.cart_id, product_id)

        # Decrement stock
        product.quantity -= quantity
        if product.quantity == 0:
            product.status = 3 # Sold Out

        if item:
            item.quantity += quantity
        else:
            item = ShoppingCartItem(cart_id=cart.cart_id, product_id=product_id, quantity=quantity)
            db.add(item)

        cart.last_updated = datetime.utcnow()
        db.add(cart)
        db.add(product)
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
        # Use FOR UPDATE to lock both the cart item and the product
        item = db.query(ShoppingCartItem).filter(ShoppingCartItem.cart_item_id == cart_item_id).with_for_update().first()
        if not item:
            return None
        
        product = db.query(Product).filter(Product.product_id == item.product_id).with_for_update().first()
        if not product:
            return None

        old_quantity = item.quantity
        diff = quantity - old_quantity

        if diff > 0:
            # Adding more to cart -> check and decrement stock
            if product.quantity < diff:
                raise ValueError(f"Không đủ hàng trong kho. Còn lại: {product.quantity}")
            product.quantity -= diff
        elif diff < 0:
            # Reducing quantity in cart -> increment stock back
            product.quantity += abs(diff)
        
        # Update product status based on quantity
        if product.quantity > 0 and product.status == 3:
            product.status = 1 # Back to Approved
        elif product.quantity == 0:
            product.status = 3 # Sold Out

        if quantity <= 0:
            db.delete(item)
        else:
            item.quantity = quantity
            item.added_at = datetime.utcnow()
            db.add(item)

        item.cart.last_updated = datetime.utcnow()
        db.add(product)
        db.add(item.cart)
        db.commit()
        
        if quantity > 0:
            db.refresh(item)
            return item
        return None

    def remove_item(self, db: Session, cart_item_id: int) -> bool:
        item = db.query(ShoppingCartItem).filter(ShoppingCartItem.cart_item_id == cart_item_id).with_for_update().first()
        if not item:
            return False

        # Restore stock before deleting the item
        product = db.query(Product).filter(Product.product_id == item.product_id).with_for_update().first()
        if product:
            product.quantity += item.quantity
            if product.quantity > 0 and product.status == 3:
                product.status = 1
            db.add(product)

        cart = item.cart
        db.delete(item)
        if cart:
            cart.last_updated = datetime.utcnow()
            db.add(cart)

        db.commit()
        return True

    def clear_cart(self, db: Session, user_id: int, restore_stock: bool = True) -> bool:
        cart = self.get_by_user_id(db, user_id)
        if not cart:
            return False

        items = db.query(ShoppingCartItem).filter(ShoppingCartItem.cart_id == cart.cart_id).all()
        for item in items:
            if restore_stock:
                product = db.query(Product).filter(Product.product_id == item.product_id).with_for_update().first()
                if product:
                    product.quantity += item.quantity
                    if product.quantity > 0 and product.status == 3:
                        product.status = 1
                    db.add(product)
            db.delete(item)

        cart.last_updated = datetime.utcnow()
        db.add(cart)
        db.commit()
        return True


crud_cart = CRUDShoppingCart()
