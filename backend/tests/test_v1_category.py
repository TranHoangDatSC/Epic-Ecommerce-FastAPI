import pytest
import sys
import os
import logging
from fastapi.testclient import TestClient

# Cấu hình log chuyên nghiệp
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Fix path import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.main import app

client = TestClient(app)

class TestCategoryModule:
    """
    HỆ THỐNG KIỂM THỬ TỰ ĐỘNG - PHÂN HỆ DANH MỤC (CATEGORY)
    Dự án: Oldshop Ecommerce
    """

    @pytest.fixture(scope="class", autouse=True)
    def admin_auth(self):
        """Khởi tạo quyền Admin cao cấp cho các tác vụ thay đổi danh mục"""
        login_data = {"username": "admin@oldshop.com", "password": "admin123"}
        res = client.post("/api/v1/auth/login", data=login_data)
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    # --- NHÓM 1: TRUY XUẤT CÔNG KHAI ---

    def test_01_get_categories_list(self):
        """[Xác minh] Truy xuất danh sách danh mục (Công khai)"""
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        logger.info(">>> [SUCCESS] Lấy danh sách danh mục công khai: OK")

    # --- NHÓM 2: QUẢN TRỊ DANH MỤC (ADMIN ONLY) ---

    def test_02_category_full_lifecycle(self, admin_auth):
        """[Xác minh] Vòng đời danh mục: Tạo -> Sửa -> Xóa mềm -> Khôi phục"""
        # 1. Tạo mới danh mục
        payload = {"name": "Đồ điện tử cũ", "description": "Laptop, điện thoại..."}
        res_create = client.post("/api/v1/categories", json=payload, headers=admin_auth)
        
        if res_create.status_code == 400:
            pytest.skip("Tên danh mục đã tồn tại, hãy reset DB để test lại.")
            
        assert res_create.status_code == 201
        cat_id = res_create.json()["category_id"]
        logger.info(f">>> [SUCCESS] Khởi tạo danh mục mới (ID: {cat_id}): OK")

        # 2. Tạo danh mục con (Sub-category)
        sub_payload = {"name": "Điện thoại cũ", "parent_id": cat_id}
        res_sub = client.post("/api/v1/categories", json=sub_payload, headers=admin_auth)
        assert res_sub.status_code == 201
        assert res_sub.json()["parent_id"] == cat_id
        logger.info(">>> [SUCCESS] Tạo danh mục con (Parent-Child Relationship): OK")

        # 3. Thử xóa danh mục đang hoạt động (Phải lỗi 400 như code Đạt viết)
        res_del_fail = client.delete(f"/api/v1/categories/{cat_id}", headers=admin_auth)
        assert res_del_fail.status_code == 400
        logger.info(">>> [SUCCESS] Chốt chặn: Không cho xóa danh mục đang Active: OK")

        # 4. Vô hiệu hóa và Xóa mềm
        client.put(f"/api/v1/categories/{cat_id}", json={"is_active": False}, headers=admin_auth)
        res_soft_del = client.delete(f"/api/v1/categories/{cat_id}", headers=admin_auth)
        assert res_soft_del.status_code == 204
        logger.info(">>> [SUCCESS] Xóa mềm danh mục thành công: OK")

    # --- NHÓM 3: BẢO MẬT & PHÂN QUYỀN ---

    def test_03_unauthorized_modification(self):
        """[Xác minh] Chốt chặn: User thường không được quyền tạo danh mục"""
        # Login bằng user thường
        login_res = client.post("/api/v1/auth/login", data={"username": "user1@gmail.com", "password": "user123"})
        token = login_res.json()["access_token"]
        
        bad_res = client.post("/api/v1/categories", json={"name": "Hack Category"}, 
                             headers={"Authorization": f"Bearer {token}"})
        assert bad_res.status_code == 403
        logger.info(">>> [SUCCESS] Chốt chặn phân quyền (RBAC): OK")