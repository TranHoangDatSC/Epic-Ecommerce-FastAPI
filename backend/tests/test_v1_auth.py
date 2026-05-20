import pytest
import sys
import os
import time
import logging
from fastapi.testclient import TestClient

# Cấu hình log để xuất kết quả đẹp
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Fix path import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.main import app

client = TestClient(app)

class TestAuthModule:
    """
    HỆ THỐNG KIỂM THỬ TỰ ĐỘNG - PHÂN HỆ XÁC THỰC (AUTH)
    Dự án: Oldshop Ecommerce
    """

    # --- NHÓM 1: ĐĂNG KÝ TÀI KHOẢN (REGISTER) ---

    def test_01_register_new_user(self):
        """[Xác minh] Đăng ký tài khoản người dùng mới thành công"""
        uid = int(time.time())
        register_payload = {
            "email": f"tester_{uid}@gmail.com",
            "password": "password123",
            "full_name": "QA Automation User",
            "phone_number": "0901112223",
            "address": "TP.HCM"
        }
        response = client.post("/api/v1/auth/register", json=register_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == register_payload["email"]
        logger.info(f">>> [SUCCESS] Đăng ký User mới (Email: {data['email']}): OK")

    def test_02_register_lock_duplicate_email(self):
        """[Xác minh] Chặn đăng ký khi Email đã tồn tại (Sử dụng data seeding: user1@gmail.com)"""
        payload = {
            "email": "user1@gmail.com",
            "password": "anypassword",
            "full_name": "Trùng Email"
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 400
        logger.info(">>> [SUCCESS] Chốt chặn trùng lặp Email: OK")

    # --- NHÓM 2: ĐĂNG NHẬP (LOGIN) ---

    @pytest.mark.parametrize("email,password,expected_status", [
        ("admin@oldshop.com", "admin123", 200),
        ("mod1@oldshop.com", "mod123", 200),
        ("user1@gmail.com", "user123", 200),
        ("user1@gmail.com", "wrongpass", 401),
        ("nonexistent@gmail.com", "pass", 401),
    ])
    def test_03_login_scenarios(self, email, password, expected_status):
        """[Xác minh] Các kịch bản Đăng nhập (Admin, Mod, User, Sai pass)"""
        login_data = {"username": email, "password": password}
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == expected_status
        if expected_status == 200:
            assert "access_token" in response.json()
            logger.info(f">>> [SUCCESS] Đăng nhập tài khoản {email}: OK")
        else:
            logger.info(f">>> [SUCCESS] Chặn đăng nhập sai cho {email}: OK")

    # --- NHÓM 3: THÔNG TIN CÁ NHÂN (GET ME) ---

    def test_04_get_me_profile(self):
        """[Xác minh] Lấy thông tin cá nhân sau khi đăng nhập thành công"""
        # 1. Login lấy token
        login_res = client.post("/api/v1/auth/login", data={"username": "user2@gmail.com", "password": "user123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get Me
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user2@gmail.com"
        # Kiểm tra logic gán role_id mặc định hoặc lấy từ DB
        assert "user_roles" in data or "role_id" in data
        logger.info(">>> [SUCCESS] Truy xuất Profile người dùng (/me): OK")

# -> python -m pytest tests/test_v1_auth.py -s -v -p no:warnings