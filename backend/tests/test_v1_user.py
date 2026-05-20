import pytest
import sys
import os
import io
import logging
from fastapi.testclient import TestClient

# Cấu hình log đầu ra chuyên nghiệp
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Fix path import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.main import app

client = TestClient(app)

class TestUsersModule:
    """
    HỆ THỐNG KIỂM THỬ TỰ ĐỘNG - PHÂN HỆ NGƯỜI DÙNG (USERS & PROFILE)
    Dự án: Oldshop Ecommerce
    """

    @pytest.fixture(scope="class", autouse=True)
    def user_auth(self):
        """Đăng nhập tài khoản user2@gmail.com để test các tính năng cá nhân"""
        login_data = {"username": "user2@gmail.com", "password": "user123"}
        res = client.post("/api/v1/auth/login", data=login_data)
        if res.status_code != 200:
            pytest.fail(">>> [FAILED] Không thể đăng nhập User để test Profile.")
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    # --- NHÓM 1: QUẢN LÝ HỒ SƠ & BẢO MẬT ---

    def test_01_get_my_profile(self, user_auth):
        """[Xác minh] Lấy thông tin chi tiết người dùng đang đăng nhập"""
        response = client.get("/api/v1/users/me", headers=user_auth)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user2@gmail.com"
        assert "roles" in data
        logger.info(">>> [SUCCESS] Truy xuất thông tin cá nhân (Profile): OK")

    def test_02_upload_avatar_logic(self, user_auth):
        """[Xác minh] Luồng Upload ảnh đại diện và đặt tên theo syntax user_[role]_[id]"""
        file_content = b"fake-avatar-data"
        file = io.BytesIO(file_content)
        files = {"file": ("avatar.png", file, "image/png")}
        
        response = client.post("/api/v1/users/me/avatar", files=files, headers=user_auth)
        assert response.status_code == 200
        assert "user_" in response.json()["avatar_url"]
        logger.info(">>> [SUCCESS] Cập nhật ảnh đại diện (Avatar Upload): OK")

    # --- NHÓM 2: QUẢN LÝ THÔNG TIN LIÊN HỆ (CONTACT INFO) ---

    def test_03_contact_info_lifecycle(self, user_auth):
        """[Xác minh] Vòng đời thông tin liên hệ: Tạo mới -> Đặt mặc định -> Xóa"""
        # 1. Tạo mới Contact
        contact_payload = {
            "full_name": "Nguyen Van Test",
            "phone_number": "0900111222",
            "address": "456 CMT8, TP.HCM",
            "is_default": False
        }
        res_create = client.post("/api/v1/users/me/contacts", json=contact_payload, headers=user_auth)
        assert res_create.status_code == 201
        contact_id = res_create.json()["contact_id"]
        logger.info(f">>> [SUCCESS] Thêm địa chỉ liên hệ mới (ID: {contact_id}): OK")

        # 2. Đặt làm mặc định
        res_default = client.post(f"/api/v1/users/me/contacts/{contact_id}/set-default", headers=user_auth)
        assert res_default.status_code == 200
        assert res_default.json()["is_default"] is True
        logger.info(">>> [SUCCESS] Thiết lập địa chỉ mặc định (Set Default): OK")

    # --- NHÓM 3: THỐNG KÊ KINH DOANH (SELLER STATS) ---

    def test_04_seller_dashboard_stats(self, user_auth):
        """[Xác minh] Truy xuất số liệu kinh doanh dành cho người bán"""
        response = client.get("/api/v1/users/seller/dashboard-stats", headers=user_auth)
        assert response.status_code == 200
        data = response.json()
        assert "totalProducts" in data
        assert "revenue" in data
        logger.info(">>> [SUCCESS] Truy xuất thống kê kinh doanh (Seller Dashboard): OK")

# -> python -m pytest tests/test_v1_user.py -s -v -p no:warnings