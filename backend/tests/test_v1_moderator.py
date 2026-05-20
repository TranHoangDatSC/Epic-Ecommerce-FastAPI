import pytest
import sys
import os
import logging
from fastapi.testclient import TestClient

# Cấu hình log đầu ra sạch
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Fix path để nhận diện module app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.main import app

client = TestClient(app)

class TestModeratorModule:
    """
    HỆ THỐNG KIỂM THỬ TỰ ĐỘNG - PHÂN HỆ KIỂM DUYỆT (MODERATOR)
    """

    @pytest.fixture(scope="class", autouse=True)
    def mod_auth(self):
        """Khởi tạo quyền Moderator cho toàn bộ module test"""
        login_data = {"username": "mod1@oldshop.com", "password": "mod123"}
        res = client.post("/api/v1/auth/login", data=login_data)
        if res.status_code != 200:
            pytest.fail(">>> [FAILED] Không thể đăng nhập Moderator.")
        
        token = res.json()["access_token"]
        logger.info("\n>>> [XÁC THỰC] Đăng nhập quyền Moderator thành công.")
        return {"Authorization": f"Bearer {token}"}

    # --- CÁC HÀM TEST PHẢI BẮT ĐẦU BẰNG test_ ---

    def test_01_pending_products(self, mod_auth):
        """[Xác minh] Truy xuất danh sách sản phẩm chờ duyệt"""
        response = client.get("/api/v1/moderator/products/pending", headers=mod_auth)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        logger.info(">>> [SUCCESS] Truy xuất danh sách sản phẩm chờ duyệt: OK")

    def test_02_user_management(self, mod_auth):
        """[Xác minh] Luồng quản lý User: Khóa/Mở tài khoản"""
        # ID 4 là user2@gmail.com từ bản seeding của bạn
        user_id = 4 
        
        # 1. Khóa
        lock_payload = {"action": "lock", "reason": "Vi phạm quy định đăng tin"}
        res_lock = client.post(f"/api/v1/moderator/users/{user_id}/lock-unlock", json=lock_payload, headers=mod_auth)
        assert res_lock.status_code == 200
        logger.info(f">>> [SUCCESS] Khóa tài khoản User (ID: {user_id}): OK")

        # 2. Mở khóa
        unlock_payload = {"action": "unlock", "reason": "Đã xử lý khiếu nại"}
        res_unlock = client.post(f"/api/v1/moderator/users/{user_id}/lock-unlock", json=unlock_payload, headers=mod_auth)
        assert res_unlock.status_code == 200
        logger.info(f">>> [SUCCESS] Kích hoạt lại tài khoản User (ID: {user_id}): OK")

    def test_03_security_rbac(self):
        """[Xác minh] Chốt chặn bảo mật khi truy cập không có quyền"""
        response = client.get("/api/v1/moderator/products/pending")
        assert response.status_code == 401
        logger.info(">>> [SUCCESS] Chốt chặn truy cập trái phép: OK")