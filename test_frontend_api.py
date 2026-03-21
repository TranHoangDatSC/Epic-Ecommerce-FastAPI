#!/usr/bin/env python3
"""
Test script to verify frontend API calls work correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_products_api():
    """Test products API with and without authentication"""

    print("Testing products API...")

    # Test 1: Get products without auth (should work)
    try:
        response = requests.get(f"{BASE_URL}/products")
        print(f"GET /products (no auth): {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"  - Found {len(products)} products")
            if products:
                print(f"  - Sample product: {products[0]['title']} (seller_id: {products[0]['seller_id']})")
        else:
            print(f"  - Error: {response.text}")
    except Exception as e:
        print(f"  - Error: {e}")

    # Test 2: Login as user1 (seller_id = 3)
    try:
        login_data = {"username": "user1@gmail.com", "password": "user123"}
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"\nLogin as user1: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # Test 3: Get products with auth (should filter out user's own products)
            response = requests.get(f"{BASE_URL}/products", headers=headers)
            print(f"GET /products (with auth): {response.status_code}")
            if response.status_code == 200:
                products = response.json()
                print(f"  - Found {len(products)} products after filtering")
                if products:
                    print(f"  - Sample product: {products[0]['title']} (seller_id: {products[0]['seller_id']})")

                    # Check if any product has seller_id = 3 (user1's seller_id)
                    user_products = [p for p in products if p['seller_id'] == 3]
                    if user_products:
                        print(f"  - WARNING: Found {len(user_products)} products owned by user1!")
                        for p in user_products:
                            print(f"    - {p['title']} (seller_id: {p['seller_id']})")
                    else:
                        print("  - GOOD: No products owned by user1 found in shop")
                else:
                    print("  - No products found")
            else:
                print(f"  - Error: {response.text}")
        else:
            print(f"  - Login failed: {response.text}")
    except Exception as e:
        print(f"  - Error: {e}")

if __name__ == "__main__":
    test_products_api()