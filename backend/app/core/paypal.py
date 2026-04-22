from decimal import Decimal
import httpx
import base64
from app.config import settings
from fastapi import HTTPException

async def get_paypal_access_token():
    """Lấy Access Token từ PayPal API"""
    url = f"{settings.PAYPAL_API_URL}/v1/oauth2/token"
    
    # Encode ClientID:Secret sang Base64
    auth_str = f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_SECRET}"
    auth_base64 = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not authenticate with PayPal")
        
    return response.json().get("access_token")

async def capture_paypal_order(paypal_order_id: str):
    """Xác nhận thanh toán từ PayPal sau khi User đã duyệt trên Frontend"""
    
    access_token = await get_paypal_access_token()
    url = f"{settings.PAYPAL_API_URL}/v2/checkout/orders/{paypal_order_id}/capture"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)

    if response.status_code not in [200, 201]:
        # Log lỗi chi tiết nếu cần nghiên cứu Fraud
        print(f"PayPal Error: {response.text}")
        return {"status": "FAILED", "details": response.json()}

    return response.json()

def convert_vnd_to_usd(amount_vnd: Decimal):
    rate = 25400  # Tỷ giá tạm tính hoặc lấy từ API ngân hàng
    return round(amount_vnd / rate, 2)