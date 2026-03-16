import requests

url = "http://127.0.0.1:8000/api/v1/auth/register"
payload = {
    "email": "test422_new@test.com",
    "password": "password123",
    "full_name": "Test User 422",
    "role_id": 3
}
response = requests.post(url, json=payload)
print(response.status_code)
print(response.text)
