import pytest
import sys
import os
import io
import logging
from fastapi.testclient import TestClient

# Cấu hình log sạch
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Fix path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.main import app

client = TestClient(app)

class TestProductModule:
    """
    HỆ THỐNG KIỂM THỬ TỰ ĐỘNG - PHÂN HỆ SẢN PHẨM & MEDIA
    """

    @pytest.fixture(scope="class")
    def seller_auth(self):
        """Token của người bán (user1@gmail.com)"""
        res = client.post("/api/v1/auth/login", data={"username": "user1@gmail.com", "password": "user123"})
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    @pytest.fixture(scope="class")
    def mod_auth(self):
        """Token của kiểm duyệt viên (mod1@oldshop.com)"""
        res = client.post("/api/v1/auth/login", data={"username": "mod1@oldshop.com", "password": "mod123"})
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    def test_01_moderator_approve_flow(self, mod_auth):
        """[Xác minh] Moderator phê duyệt sản phẩm"""
        # Lấy danh sách sản phẩm đang chờ duyệt
        pending_res = client.get("/api/v1/products/pending/all", headers=mod_auth)
        if not pending_res.json():
            pytest.skip("Không có sản phẩm chờ duyệt để test.")
            
        target_id = pending_res.json()[0]["product_id"]
        
        # Thực hiện phê duyệt
        res_approve = client.post(f"/api/v1/products/{target_id}/approve", headers=mod_auth)
        assert res_approve.status_code == 200
        assert res_approve.json()["status"] == 1
        logger.info(f">>> [SUCCESS] Moderator phê duyệt sản phẩm thành công: OK")

    def test_02_reject_product_with_reason(self, mod_auth):
        """[Xác minh] Chốt chặn: Từ chối sản phẩm phải có lý do ít nhất 10 ký tự"""
        # Thử reject không đủ 10 ký tự lý do
        res_fail = client.post("/api/v1/products/1/reject?reject_reason=Short", headers=mod_auth)
        assert res_fail.status_code == 422 # Lỗi Validation của FastAPI
        logger.info(">>> [SUCCESS] Chốt chặn độ dài lý do từ chối: OK")

    def test_03_increment_view_count(self):
        """[Xác minh] Tự động tăng lượt xem khi xem chi tiết sản phẩm"""
        # Lấy view hiện tại của sản phẩm ID 1
        p1 = client.get("/api/v1/products/1").json()
        initial_views = p1.get("view_count", 0)
        
        # Xem lại lần nữa
        client.get("/api/v1/products/1")
        p2 = client.get("/api/v1/products/1").json()
        
        assert p2.get("view_count", 0) == initial_views + 2
        logger.info(">>> [SUCCESS] Tự động tăng View Count khi truy cập: OK")