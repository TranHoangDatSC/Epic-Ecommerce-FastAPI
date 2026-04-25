from app import models
from app.models import Transaction
from app.models import PaymentMethod
from app.models import User
from app.models import OrderDetail
from app.models import Product
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime
from app.crud.base import CRUDBase
from app.models import Order
from app.schemas import OrderCreate, OrderUpdate
from decimal import Decimal
import uuid

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
        def get_sellers_by_order(self, db: Session, order_id: int) -> List[int]:
            """
            Lấy danh sách seller_id duy nhất từ tất cả sản phẩm trong một đơn hàng.
            """
            sellers = (
                db.query(Product.seller_id)
                .join(OrderDetail, Product.product_id == OrderDetail.product_id)
                .filter(OrderDetail.order_id == order_id)
                .distinct()
                .all()
            )
            return [s[0] for s in sellers]

    def get_by_seller(self, db: Session, seller_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Lấy tất cả đơn hàng chứa sản phẩm của người bán này"""
        return (
            db.query(Order)
            .join(OrderDetail) 
            .join(Product)     
            .filter(Product.seller_id == seller_id)     
            .filter(Order.is_deleted == False)
            .order_by(Order.order_date.desc())
            .distinct() 
            .offset(skip)
            .limit(limit)
            .all()
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

    def get_sellers_by_order(self, db: Session, order_id: int) -> List[int]:
        """ Lấy danh sách seller_id duy nhất từ tất cả sản phẩm trong một đơn hàng. """
        sellers = (
            db.query(Product.seller_id)
            .join(OrderDetail, Product.product_id == OrderDetail.product_id)
            .filter(OrderDetail.order_id == order_id)
            .distinct()
            .all()
        )
        return [s[0] for s in sellers]

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
        self, db: Session, buyer_id: int, contact_id: int, payment_method_id: int, 
        order_items: List[dict], shipping_fee: Decimal = Decimal("0"), 
        discount_amount: Decimal = Decimal("0"), voucher_id: Optional[int] = None, 
        notes: Optional[str] = None, shipping_address: Optional[str] = None, 
        phone_number: Optional[str] = None
    ) -> Order:
        from app.models import OrderDetail, Product, Transaction
        from app.core.fraud_detection import verify_transaction_ml
        import uuid

        # 1. Tính toán tiền bạc
        total_amount = Decimal("0")
        for item in order_items:
            product = db.query(Product).filter(Product.product_id == item['product_id']).first()
            if product:
                total_amount += product.price * Decimal(str(item['quantity']))

        final_amount = total_amount - discount_amount + shipping_fee

        # 2. Tạo đơn hàng (Trạng thái mặc định là PENDING - 0)
        order = Order(
            buyer_id=buyer_id, contact_id=contact_id, payment_method_id=payment_method_id,
            voucher_id=voucher_id, total_amount=total_amount, shipping_fee=shipping_fee,
            discount_amount=discount_amount, final_amount=final_amount, notes=notes,
            shipping_address=shipping_address, tracking_number=phone_number,
            order_status=0, is_deleted=False
        )
        db.add(order)
        db.flush() 

        # 3. Lấy số dư thực tế để chạy ML (Đây là bước ép balance thực)
        user = db.query(models.User).filter(models.User.user_id == buyer_id).first()
        db.refresh(user) 
        current_balance = user.balance if user else Decimal("0")

        # CHẠY ML NGAY LÚC NÀY
        ml_check = verify_transaction_ml(final_amount, current_balance)

        # 4. Tạo Transaction kèm theo Fraud Score
        new_trans = Transaction(
            order_id=order.order_id,
            user_id=buyer_id,
            payment_method_id=payment_method_id,
            amount=final_amount,
            balance_before=current_balance,
            balance_after=current_balance, # Chưa trừ vì đơn đang Pending
            reference_number=f"REF-{uuid.uuid4().hex[:8].upper()}-{order.order_id}",
            transaction_status=0,
            address=f"{order.shipping_address}",
            fraud_score=ml_check["score"] # Ghi điểm số vào đây
        )
        db.add(new_trans)

        # 5. Thêm chi tiết đơn hàng
        for item in order_items:
            product = db.query(Product).filter(Product.product_id == item['product_id']).first()
            if product:
                db.add(OrderDetail(
                    order_id=order.order_id, product_id=item['product_id'],
                    quantity=item['quantity'], price_at_purchase=product.price,
                    subtotal=product.price * Decimal(str(item['quantity']))
                ))

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
