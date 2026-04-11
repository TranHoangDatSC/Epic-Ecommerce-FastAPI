import pytest
from fastapi.testclient import TestClient
from app.main import app  # Import instance FastAPI của bạn

client = TestClient(app)

# Biến để lưu token và ID dùng chung cho các test case
state = {
    "token": None,
    "mod_id": None
}

def test_login_admin():
    """Test đăng nhập quyền admin để lấy token"""
    login_data = {
        "username": "admin@oldshop.com",
        "password": "admin123"
    }
    # Lưu ý: Nếu dùng OAuth2 Password Bearer, dùng data= thay vì json=
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200
    state["token"] = response.json().get("access_token")
    assert state["token"] is not None

def test_list_moderators():
    """Test lấy danh sách moderator"""
    headers = {"Authorization": f"Bearer {state['token']}"}
    response = client.get("/api/v1/admin/moderators", headers=headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_moderator():
    """Test tạo mới moderator"""
    headers = {"Authorization": f"Bearer {state['token']}"}
    new_mod = {
        "username": "test_mod_pytest",
        "email": "pytest_mod@gmail.com",
        "password": "testpassword123",
        "full_name": "Pytest Moderator",
        "phone_number": "0123456789",
        "address": "Hanoi, Vietnam"
    }
    response = client.post("/api/v1/admin/moderators", json=new_mod, headers=headers)
    
    # Nếu user đã tồn tại có thể trả về 400 hoặc 200 tùy logic của bạn
    assert response.status_code in [200, 201]
    data = response.json()
    state["mod_id"] = data.get("user_id")
    assert data["username"] == "test_mod_pytest"

def test_toggle_moderator_status():
    """Test khóa và mở khóa moderator"""
    if not state["mod_id"]:
        pytest.skip("Không có mod_id để test")
        
    headers = {"Authorization": f"Bearer {state['token']}"}
    
    # 1. Khóa
    lock_payload = {"action": "lock", "reason": "Test khóa"}
    res_lock = client.patch(f"/api/v1/admin/moderators/{state['mod_id']}/status", 
                            json=lock_payload, headers=headers)
    assert res_lock.status_code == 200
    assert res_lock.json()["is_active"] is False

    # 2. Mở khóa
    unlock_payload = {"action": "unlock", "reason": "Test mở"}
    res_unlock = client.patch(f"/api/v1/admin/moderators/{state['mod_id']}/status", 
                              json=unlock_payload, headers=headers)
    assert res_unlock.status_code == 200
    assert res_unlock.json()["is_active"] is True