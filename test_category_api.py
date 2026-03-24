#!/usr/bin/env python3
"""
Test script for Category Management API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_category_endpoints():
    """Test all category management endpoints"""

    # Test 1: Get active categories
    print("1. Testing GET /categories (active only)")
    response = requests.get(f"{BASE_URL}/categories")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        categories = response.json()
        print(f"Found {len(categories)} active categories")
    else:
        print(f"Error: {response.text}")

    # Test 2: Get categories with deleted
    print("\n2. Testing GET /categories (include deleted)")
    response = requests.get(f"{BASE_URL}/categories?include_deleted=true")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        all_categories = response.json()
        print(f"Found {len(all_categories)} total categories")
        deleted_count = sum(1 for cat in all_categories if cat.get('is_deleted', False))
        print(f"Found {deleted_count} deleted categories")
    else:
        print(f"Error: {response.text}")

    # Test 3: Create a test category
    print("\n3. Testing POST /categories (create)")
    test_category = {
        "name": "Test Category API",
        "description": "Category created for API testing",
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/categories", json=test_category)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        created_cat = response.json()
        category_id = created_cat['category_id']
        print(f"Created category with ID: {category_id}")
    else:
        print(f"Error: {response.text}")
        return

    # Test 4: Soft delete the category
    print("\n4. Testing DELETE /categories/{id} (soft delete)")
    response = requests.delete(f"{BASE_URL}/categories/{category_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print("Category soft deleted successfully")
    else:
        print(f"Error: {response.text}")

    # Test 5: Check if category appears in deleted list
    print("\n5. Testing GET /categories (include deleted after soft delete)")
    response = requests.get(f"{BASE_URL}/categories?include_deleted=true")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        all_categories = response.json()
        deleted_cats = [cat for cat in all_categories if cat.get('is_deleted', False)]
        test_cat_deleted = any(cat['category_id'] == category_id and cat['is_deleted'] for cat in deleted_cats)
        print(f"Test category found in deleted list: {test_cat_deleted}")

    # Test 6: Restore the category
    print("\n6. Testing POST /categories/{id}/restore")
    response = requests.post(f"{BASE_URL}/categories/{category_id}/restore")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        restored_cat = response.json()
        print(f"Category restored: {restored_cat['name']}")
    else:
        print(f"Error: {response.text}")

    # Test 7: Hard delete the category
    print("\n7. Testing DELETE /categories/{id}/hard-delete")
    # First soft delete again
    requests.delete(f"{BASE_URL}/categories/{category_id}")
    # Then hard delete
    response = requests.delete(f"{BASE_URL}/categories/{category_id}/hard-delete")
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print("Category hard deleted successfully")
    else:
        print(f"Error: {response.text}")

    # Test 8: Verify hard delete
    print("\n8. Testing GET /categories (verify hard delete)")
    response = requests.get(f"{BASE_URL}/categories?include_deleted=true")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        all_categories = response.json()
        test_cat_exists = any(cat['category_id'] == category_id for cat in all_categories)
        print(f"Test category still exists: {test_cat_exists}")

    print("\nAPI Testing completed!")

if __name__ == "__main__":
    test_category_endpoints()