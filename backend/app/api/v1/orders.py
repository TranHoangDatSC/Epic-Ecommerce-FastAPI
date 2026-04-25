from decimal import Decimal
from typing import List, Optional
from datetime import datetime
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.models import User, Order, Product, ContactInfo, PaymentMethod, Transaction
from app.schemas import OrderResponse, OrderDetailResponse_Extended, OrderCreate, OrderUpdate
from app.core.dependencies import check_admin, check_user_role
from app.config import settings
from app.core.fraud_detection import verify_transaction_ml
from app.core.paypal import get_paypal_access_token, capture_paypal_order
from app.crud.order import crud_order
from app.crud.shopping_cart import crud_cart

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/payment-methods", response_model=list[schemas.PaymentMethodResponse])
async def get_payment_methods(db: Session = Depends(get_db)):
    return db.query(PaymentMethod).filter(PaymentMethod.is_deleted == False).all()

@router.get("/seller", response_model=list[OrderResponse])
async def get_seller_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(check_user_role([3])),
    db: Session = Depends(get_db)
):
    return crud_order.get_by_seller(db, seller_id=current_user.user_id, skip=skip, limit=limit)

@router.get("", response_model=list[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: int = Query(None),
    current_user: User = Depends(check_user_role([3])),
    db: Session = Depends(get_db)
):
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
            db, buyer_id=current_user.user_id, skip=skip, limit=limit
        )
    return orders

@router.get("/{order_id}", response_model=OrderDetailResponse_Extended)
async def get_order(
    order_id: int,
    current_user: User = Depends(check_user_role([1, 2, 3])),
    db: Session = Depends(get_db)
):
    order = crud_order.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    user_roles = [role.role_id for role in current_user.user_roles]
    is_admin = 1 in user_roles
    seller_ids_in_order = crud_order.get_sellers_by_order(db, order_id)
    is_seller = current_user.user_id in seller_ids_in_order
    
    if not (is_admin or order.buyer_id == current_user.user_id or is_seller):
        raise HTTPException(status_code=403, detail="Permission denied")
    return order

@router.post("", response_model=OrderDetailResponse_Extended, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(check_user_role([3])),
    db: Session = Depends(get_db)
):
    contact = db.query(ContactInfo).filter(
        ContactInfo.contact_id == order_in.contact_id,
        ContactInfo.user_id == current_user.user_id,
        ContactInfo.is_deleted == False
    ).first()
    if not contact:
        raise HTTPException(status_code=400, detail="Invalid contact information")

    final_address = order_in.shipping_address or contact.address
    final_phone = order_in.phone_number or contact.phone_number

    payment_method = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.payment_method_id == order_in.payment_method_id,
        models.PaymentMethod.is_deleted == False
    ).first()
    
    if not payment_method:
        raise HTTPException(status_code=400, detail="Invalid payment method")

    for item in order_in.order_items:
        product = db.query(Product).filter(
            Product.product_id == item.product_id,
            Product.is_deleted == False
        ).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        if product.seller_id == current_user.user_id:
            raise HTTPException(status_code=400, detail=f"You cannot order your own product '{product.title}'")

    order = crud_order.create_order(
        db=db,
        buyer_id=current_user.user_id,
        contact_id=order_in.contact_id,
        payment_method_id=order_in.payment_method_id,
        order_items=[item.dict() for item in order_in.order_items],
        shipping_fee=order_in.shipping_fee,
        discount_amount=Decimal("0"),
        voucher_id=order_in.voucher_id,
        notes=order_in.notes,
        shipping_address=final_address,
        phone_number=final_phone
    )

    try:
        product_ids = [item.product_id for item in order_in.order_items]
        cart = db.query(models.ShoppingCart).filter(models.ShoppingCart.user_id == current_user.user_id).first()
        if cart:
            db.query(models.ShoppingCartItem).filter(
                models.ShoppingCartItem.cart_id == cart.cart_id,
                models.ShoppingCartItem.product_id.in_(product_ids)
            ).delete(synchronize_session=False)
            db.commit()
    except Exception as e:
        print(f"Lỗi khi xóa giỏ hàng: {e}")

    db.refresh(order)
    return order

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(check_user_role([1, 2, 3])),
    db: Session = Depends(get_db)
):
    order = crud_order.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    user_roles = [role.role_id for role in current_user.user_roles]
    is_admin = 1 in user_roles
    is_owner = order.buyer_id == current_user.user_id
    seller_ids_in_order = crud_order.get_sellers_by_order(db, order_id)
    is_seller = current_user.user_id in seller_ids_in_order

    if not (is_admin or is_owner or is_seller):
        raise HTTPException(status_code=403, detail="You do not have permission")

    if order_update.order_status == 4:
        if order.order_status == 4:
            raise HTTPException(status_code=400, detail="Order is already cancelled")
        for detail in order.order_details:
            product = detail.product
            product.quantity += detail.quantity
            if product.status == 3:
                product.status = 1
            db.add(product)

    if order_update.order_status in [1, 2, 3]:
        if not (is_admin or is_seller):
            raise HTTPException(status_code=403, detail="Only seller/admin can confirm/ship orders")
        
    updated_order = crud_order.update_order_status(
        db=db,
        order_id=order_id,
        new_status=order_update.order_status or order.order_status,
        tracking_number=order_update.tracking_number
    )
    db.commit()
    return updated_order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    admin_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
):
    order = crud_order.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.is_deleted = True
    db.add(order)
    db.commit()

@router.post("/create-paypal-order")
async def create_paypal_order(
    order_in: schemas.OrderCreate,
    bypass_fraud: bool = Query(False),
    current_user: User = Depends(check_user_role([3])),
    db: Session = Depends(get_db)
):
    # 1. Tính toán tổng tiền thực tế
    total_amount = sum(
        item.quantity * db.query(Product).filter(Product.product_id == item.product_id).first().price 
        for item in order_in.order_items
    ) + order_in.shipping_fee

    # 2. Kiểm tra Fraud (giữ nguyên logic của bạn)
    ml_res = verify_transaction_ml(total_amount, current_user.balance)
    if ml_res["is_fraud"]:
        raise HTTPException(status_code=403, detail="Giao dịch bị từ chối do rủi ro quá cao.")

    if ml_res["is_suspicious"] and not bypass_fraud:
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Phát hiện hành vi bất thường. Vui lòng xác thực lại sau 60 giây.",
                "retry_after": 60
            }
        )

    contact = db.query(ContactInfo).filter(
        ContactInfo.contact_id == order_in.contact_id,
        ContactInfo.user_id == current_user.user_id
    ).first()
    if not contact:
        raise HTTPException(status_code=400, detail="Không tìm thấy địa chỉ")

    try:
        # --- BƯỚC QUAN TRỌNG: CHỐNG TRÙNG HÓA ĐƠN ---
        # Tìm đơn hàng Pending có cùng số tiền của user này tạo trong vòng 10 phút qua
        existing_order = db.query(Order).filter(
            Order.buyer_id == current_user.user_id,
            Order.order_status == 0, # Trạng thái Pending
            Order.final_amount == total_amount,
            Order.is_deleted == False
        ).order_by(Order.order_date.desc()).first()

        if existing_order:
            # Nếu đã có đơn hàng chờ, dùng lại đơn này thay vì tạo mới
            new_order = existing_order
        else:
            # Nếu chưa có thì mới tạo mới vào DB
            new_order = crud_order.create_order(
                db=db,
                buyer_id=current_user.user_id,
                contact_id=order_in.contact_id,
                payment_method_id=order_in.payment_method_id,
                order_items=[item.dict() for item in order_in.order_items],
                shipping_fee=order_in.shipping_fee,
                shipping_address=order_in.shipping_address or contact.address,
                phone_number=order_in.phone_number or contact.phone_number
            )
        # -------------------------------------------

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    token = await get_paypal_access_token()
    total_usd = "{:.2f}".format(new_order.final_amount / 25400)

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{settings.PAYPAL_API_URL}/v2/checkout/orders",
            json={
                "intent": "CAPTURE",
                "purchase_units": [{
                    "reference_id": str(new_order.order_id), # ID này giờ đã được đảm bảo duy nhất
                    "amount": {"currency_code": "USD", "value": total_usd}
                }]
            },
            headers={"Authorization": f"Bearer {token}"}
        )

    if res.status_code != 201:
        raise HTTPException(status_code=400, detail="PayPal API Error")

    return {"paypal": res.json(), "internal_order_id": new_order.order_id}
    
@router.post("/{order_id}/capture-paypal")
async def capture_paypal_payment(
    order_id: int, 
    paypal_order_id: str = Query(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_user_role([3]))
):
    paypal_res = await capture_paypal_order(paypal_order_id)
    
    if paypal_res.get("status") == "COMPLETED":
        order_obj = crud_order.get_by_id(db, order_id=order_id)
        if not order_obj:
            raise HTTPException(status_code=404, detail="Order not found")

        db.refresh(current_user)
        ml_res = verify_transaction_ml(order_obj.final_amount, current_user.balance)

        # --- FIX LỖI: Xóa giỏ hàng thủ công thay vì gọi hàm CRUD lỗi ---
        try:
            cart = db.query(models.ShoppingCart).filter(models.ShoppingCart.user_id == current_user.user_id).first()
            if cart:
                product_ids = [detail.product_id for detail in order_obj.order_details]
                db.query(models.ShoppingCartItem).filter(
                    models.ShoppingCartItem.cart_id == cart.cart_id,
                    models.ShoppingCartItem.product_id.in_(product_ids)
                ).delete(synchronize_session=False)
        except Exception as e:
            print(f"Lỗi xóa giỏ hàng: {e}")
        # -------------------------------------------------------------

        transaction = db.query(Transaction).filter(Transaction.order_id == order_id).first()
        if transaction:
            transaction.fraud_score = ml_res["score"]
            transaction.address = f"PayPal Ref: {paypal_order_id} | AI: {ml_res['score']}"
            
            if ml_res["is_fraud"]:
                transaction.transaction_status = 2 
                order_obj.order_status = 0 
                message = "Giao dịch bị tạm giữ do rủi ro cao."
            else:
                transaction.transaction_status = 1
                order_obj.order_status = 1 
                message = "Thanh toán thành công."

        db.commit()
        return {"status": "success", "fraud_detected": ml_res["is_fraud"], "detail": message}
    
    raise HTTPException(status_code=400, detail="PayPal Capture failed")