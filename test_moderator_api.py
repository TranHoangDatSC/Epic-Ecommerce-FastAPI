#!/usr/bin/env python3
"""Test script for moderator management endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def login_admin():
    """Login as admin and return access token"""
    login_data = {
        "username": "admin@oldshop.com",  # OAuth2 form uses 'username' field for email
        "password": "admin123"
    }

    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_moderator_endpoints():
    """Test the new moderator management endpoints"""

    # Login as admin
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without admin token")
        return

    headers = {"Authorization": f"Bearer {token}"}

    print("✅ Logged in as admin")

    # Test 1: List moderators
    print("\n--- Test 1: List Moderators ---")
    response = requests.get(f"{BASE_URL}/api/v1/admin/moderators", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        moderators = response.json()
        print(f"✅ Found {len(moderators)} moderators")
        for mod in moderators[:3]:  # Show first 3
            print(f"  - {mod.get('username')} ({mod.get('email')}) - Active: {mod.get('is_active')}")
    else:
        print(f"❌ Error: {response.text}")

    # Test 2: Create new moderator
    print("\n--- Test 2: Create New Moderator ---")
    new_mod_data = {
        "username": "test_mod_api",
        "email": "test_mod_api@gmail.com",
        "password": "test123",
        "full_name": "Test Moderator API",
        "phone_number": "0987654321",
        "address": "Test Address"
    }
    response = requests.post(f"{BASE_URL}/api/v1/admin/moderators", json=new_mod_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        created_mod = response.json()
        print(f"✅ Created moderator: {created_mod.get('username')}")
        mod_id = created_mod.get('user_id')
    else:
        print(f"❌ Error: {response.text}")
        mod_id = None

    # Test 3: Toggle moderator status (if we have a moderator)
    if mod_id:
        print(f"\n--- Test 3: Lock Moderator (ID: {mod_id}) ---")
        lock_data = {
            "action": "lock",
            "reason": "Testing API lock functionality"
        }
        response = requests.patch(f"{BASE_URL}/api/v1/admin/moderators/{mod_id}/status", json=lock_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            updated_mod = response.json()
            print(f"✅ Moderator status updated: Active = {updated_mod.get('is_active')}")
        else:
            print(f"❌ Error: {response.text}")

        print(f"\n--- Test 4: Unlock Moderator (ID: {mod_id}) ---")
        unlock_data = {
            "action": "unlock",
            "reason": "Testing API unlock functionality"
        }
        response = requests.patch(f"{BASE_URL}/api/v1/admin/moderators/{mod_id}/status", json=unlock_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            updated_mod = response.json()
            print(f"✅ Moderator status updated: Active = {updated_mod.get('is_active')}")
        else:
            print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_moderator_endpoints()