#!/usr/bin/env python3
"""
Test script for shopping cart API endpoints
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

def login_user(email: str, password: str) -> str:
    """Login and return access token"""
    login_data = {
        "username": email,  # OAuth2 uses 'username' field but we treat it as email
        "password": password
    }
    print(f"Attempting login with: {login_data}")
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response content: {response.text}")
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_cart_operations():
    """Test shopping cart CRUD operations"""

    print("Testing shopping cart API endpoints...")

    # Login as user1
    token = login_user("user1@gmail.com", "user123")
    if not token:
        print("Cannot login, skipping cart tests")
        return

    headers = {"Authorization": f"Bearer {token}"}
    print(f"Logged in as user1, token: {token[:20]}...")

    # Test 1: Get cart (should be empty initially)
    try:
        response = requests.get(f"{BASE_URL}/cart", headers=headers)
        print(f"GET /cart: {response.status_code}")
        if response.status_code == 200:
            cart_data = response.json()
            print(f"  - Cart: {cart_data}")
        else:
            print(f"  - Error: {response.text}")
    except Exception as e:
        print(f"  - Error: {e}")

    # Test 2: Get products first to find a product ID
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        print(f"GET /products: {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"  - Found {len(products)} products")
            if products:
                product_id = products[0]['product_id']
                print(f"  - Using product ID: {product_id}")

                # Test 3: Add item to cart
                cart_item = {
                    "product_id": product_id,
                    "quantity": 2
                }
                response = requests.post(f"{BASE_URL}/cart/items", json=cart_item, headers=headers)
                print(f"POST /cart/items: {response.status_code}")
                if response.status_code == 201:
                    print(f"  - Item added: {response.json()}")
                else:
                    print(f"  - Error: {response.text}")

                # Test 4: Get cart again (should have the item)
                response = requests.get(f"{BASE_URL}/cart", headers=headers)
                print(f"GET /cart (after add): {response.status_code}")
                if response.status_code == 200:
                    cart_data = response.json()
                    print(f"  - Cart now: {cart_data}")
    except Exception as e:
        print(f"  - Error: {e}")

    print("\nCart API test completed!")

if __name__ == "__main__":
    test_cart_operations()