import pytest
import sys
import os
import time
import logging
from fastapi.testclient import TestClient

# Cấu hình log để xuất ra giao diện đẹp hơn
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Fix path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.main import app

client = TestClient(app)

class TestAdminModule:
    """
    HỆ THỐNG KIỂM THỬ TỰ ĐỘNG - PHÂN HỆ QUẢN TRỊ (ADMIN)
    Dự án: Oldshop Ecommerce
    """

    @pytest.fixture(scope="class", autouse=True)
    def admin_auth(self):
        """Khởi tạo quyền truy cập Admin cao cấp"""
        login_data = {"username": "admin@oldshop.com", "password": "admin123"}
        response = client.post("/api/v1/auth/login", data=login_data)
        if response.status_code != 200:
            pytest.fail(">>> [FAILED] Không thể xác thực quyền Admin.")
        
        token = response.json()["access_token"]
        logger.info("\n>>> [XÁC THỰC] Đăng nhập quyền Admin thành công.")
        return {"Authorization": f"Bearer {token}"}

    # --- NHÓM 1: THỐNG KÊ HỆ THỐNG ---

    def test_01_stats_check(self, admin_auth):
        """[Xác minh] Dữ liệu thống kê Dashboard Admin"""
        response = client.get("/api/v1/admin/stats", headers=admin_auth)
        assert response.status_code == 200
        logger.info(">>> [SUCCESS] Truy xuất thống kê doanh thu và người dùng: OK")

    # --- NHÓM 2: QUẢN LÝ NHÂN SỰ (MODERATOR) ---

    def test_02_moderator_flow(self, admin_auth):
        """[Xác minh] Vòng đời tài khoản Moderator (Tạo -> Khóa -> Mở)"""
        uid = int(time.time())
        mod_payload = {
            "username": f"qa_mod_{uid}",
            "email": f"qa_{uid}@oldshop.com",
            "password": "password123",
            "full_name": "Automation Tester",
            "phone_number": "0900000000",
            "address": "Phòng Lab"
        }

        # 1. Tạo mới
        res_create = client.post("/api/v1/admin/moderators", json=mod_payload, headers=admin_auth)
        assert res_create.status_code == 200
        mod_id = res_create.json()["user_id"]
        logger.info(f">>> [SUCCESS] Khởi tạo tài khoản Moderator (ID: {mod_id}): OK")

        # 2. Khóa
        res_lock = client.patch(f"/api/v1/admin/moderators/{mod_id}/status", 
                                json={"action": "lock", "reason": "Test khóa"}, headers=admin_auth)
        assert res_lock.json()["is_active"] is False
        logger.info(f">>> [SUCCESS] Vô hiệu hóa tài khoản (Lock Account): OK")

        # 3. Mở khóa
        res_unlock = client.patch(f"/api/v1/admin/moderators/{mod_id}/status", 
                                  json={"action": "unlock", "reason": "Test mở"}, headers=admin_auth)
        assert res_unlock.json()["is_active"] is True
        logger.info(f">>> [SUCCESS] Kích hoạt lại tài khoản (Unlock Account): OK")

    # --- NHÓM 3: TOÀN VẸN DỮ LIỆU & BẢO MẬT ---

    def test_03_sql_join_integrity(self, admin_auth):
        """[Xác minh] Logic SQL Join trên Nhật ký vi phạm"""
        response = client.get("/api/v1/admin/violation-logs?limit=1", headers=admin_auth)
        assert response.status_code == 200
        if response.json():
            assert "username" in response.json()[0]
        logger.info(">>> [SUCCESS] Kiểm tra liên kết bảng (SQL Join) lấy Username: OK")

    def test_04_security_gate(self, admin_auth):
        """[Xác minh] Chốt chặn bảo mật khi thiếu Token"""
        response = client.get("/api/v1/admin/stats")
        assert response.status_code == 401
        logger.info(">>> [SUCCESS] Chốt chặn truy cập trái phép (401 Unauthorized): OK")

# -> python -m pytest tests/test_v1_admin.py -s -v -p no:warnings