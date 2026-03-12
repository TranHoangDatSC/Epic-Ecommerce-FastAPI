from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime
from app.crud.base import CRUDBase
from app.models import Order
from app.schemas import OrderCreate, OrderUpdate
from decimal import Decimal


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    """Order CRUD operations"""

    def get_by_id(self, db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .filter(Order.is_deleted == False)
            .first()
        )

    def get_by_buyer(
        self,
        db: Session,
        buyer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get all orders by buyer"""
        return (
            db.query(Order)
            .filter(Order.buyer_id == buyer_id)
            .filter(Order.is_deleted == False)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        order_status: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get orders by status"""
        return (
            db.query(Order)
            .filter(Order.order_status == order_status)
            .filter(Order.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pending_orders(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get pending orders"""
        return (
            db.query(Order)
            .filter(Order.order_status == 0)  # Pending
            .filter(Order.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_order(
        self,
        db: Session,
        buyer_id: int,
        contact_id: int,
        payment_method_id: int,
        order_items: List[dict],
        shipping_fee: Decimal = Decimal("0"),
        discount_amount: Decimal = Decimal("0"),
        voucher_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Order:
        """Create a new order with items"""
        from app.models import OrderDetail, Product
        
        # Calculate total amount
        total_amount = Decimal("0")
        for item in order_items:
            product = db.query(Product).filter(Product.product_id == item['product_id']).first()
            if product:
                total_amount += product.price * Decimal(str(item['quantity']))
        
        # Calculate final amount
        final_amount = total_amount - discount_amount + shipping_fee
        
        # Create order
        order = Order(
            buyer_id=buyer_id,
            contact_id=contact_id,
            payment_method_id=payment_method_id,
            voucher_id=voucher_id,
            total_amount=total_amount,
            shipping_fee=shipping_fee,
            discount_amount=discount_amount,
            final_amount=final_amount,
            notes=notes,
            order_status=0,  # Pending
        )
        
        db.add(order)
        db.flush()  # Get the order_id
        
        # Add order details
        for item in order_items:
            product = db.query(Product).filter(Product.product_id == item['product_id']).first()
            if product:
                order_detail = OrderDetail(
                    order_id=order.order_id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price_at_purchase=product.price,
                    subtotal=product.price * Decimal(str(item['quantity']))
                )
                db.add(order_detail)
        
        db.commit()
        db.refresh(order)
        return order

    def update_order_status(
        self,
        db: Session,
        order_id: int,
        new_status: int,
        tracking_number: Optional[str] = None
    ) -> Optional[Order]:
        """Update order status"""
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if order:
            order.order_status = new_status
            if tracking_number:
                order.tracking_number = tracking_number
            db.add(order)
            db.commit()
            db.refresh(order)
        return order

    def get_orders_by_date_range(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get orders within a date range"""
        return (
            db.query(Order)
            .filter(Order.is_deleted == False)
            .filter(and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ))
            .offset(skip)
            .limit(limit)
            .all()
        )


# Create CRUD instance
crud_order = CRUDOrder(Order)
