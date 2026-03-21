#!/usr/bin/env python3
"""
Test script for cart API with authentication
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_cart_with_auth():
    """Test cart API with authentication"""

    print("Testing cart API with authentication...")

    # Login as user1
    login_data = {"username": "user1@gmail.com", "password": "user123"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Login: {response.status_code}")

    if response.status_code != 200:
        print("Login failed!")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get cart
    response = requests.get(f"{BASE_URL}/cart", headers=headers)
    print(f"GET /cart: {response.status_code}")
    if response.status_code == 200:
        cart = response.json()
        print(f"Cart has {len(cart['cart_items'])} items")

    # Add item to cart
    cart_item = {"product_id": 3, "quantity": 1}
    response = requests.post(f"{BASE_URL}/cart/items", json=cart_item, headers=headers)
    print(f"POST /cart/items: {response.status_code}")

    # Get cart again
    response = requests.get(f"{BASE_URL}/cart", headers=headers)
    print(f"GET /cart after add: {response.status_code}")
    if response.status_code == 200:
        cart = response.json()
        print(f"Cart now has {len(cart['cart_items'])} items")

if __name__ == "__main__":
    test_cart_with_auth()