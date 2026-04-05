#!/usr/bin/env python3
"""Test script for moderator management endpoints"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[PASS]{Colors.END} {msg}")

def log_error(msg):
    print(f"{Colors.RED}[FAIL]{Colors.END} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}[WARN]{Colors.END} {msg}")

def login_admin():
    """Login as admin and return access token"""
    log_info("Attempt to login as admin...")
    login_data = {
        "username": "admin@oldshop.com",
        "password": "admin123"
    }

    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        log_success(f"Admin login successful")
        return token
    else:
        log_error(f"Admin login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_list_moderators(headers):
    """Test: List all moderators"""
    print(f"\n{Colors.BLUE}=== Test 1: List Moderators ==={Colors.END}")
    
    response = requests.get(f"{BASE_URL}/api/v1/admin/moderators", headers=headers)
    
    if response.status_code == 200:
        moderators = response.json()
        log_success(f"Retrieved {len(moderators)} moderators")
        for i, mod in enumerate(moderators[:5], 1):
            print(f"  {i}. {mod.get('username')} ({mod.get('email')}) - Active: {mod.get('is_active')}")
        return True
    else:
        log_error(f"Failed to list moderators: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_create_moderator(headers):
    """Test: Create new moderator"""
    print(f"\n{Colors.BLUE}=== Test 2: Create New Moderator ==={Colors.END}")
    
    # Generate unique username with timestamp
    timestamp = int(datetime.now().timestamp())
    new_mod_data = {
        "username": f"test_mod_{timestamp}",
        "email": f"test_mod_{timestamp}@oldshop.com",
        "password": "TestPassword123",
        "full_name": "Test Moderator API",
        "phone_number": "0987654321",
        "address": "Test Address"
    }
    
    log_info(f"Creating moderator: {new_mod_data['username']}")
    response = requests.post(f"{BASE_URL}/api/v1/admin/moderators", json=new_mod_data, headers=headers)
    
    if response.status_code == 200:
        created_mod = response.json()
        mod_id = created_mod.get('user_id')
        role_id = created_mod.get('role_id')
        
        if role_id == 2:
            log_success(f"Created moderator: {created_mod.get('username')} (ID: {mod_id}, Role: {role_id})")
            return mod_id
        else:
            log_error(f"Created user with wrong role_id: {role_id} (expected 2)")
            return None
    else:
        log_error(f"Failed to create moderator: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_lock_moderator(headers, mod_id):
    """Test: Lock moderator account"""
    print(f"\n{Colors.BLUE}=== Test 3: Lock Moderator ==={Colors.END}")
    
    lock_data = {
        "action": "lock",
        "reason": "Testing lock functionality"
    }
    
    log_info(f"Locking moderator ID: {mod_id}")
    response = requests.patch(f"{BASE_URL}/api/v1/admin/moderators/{mod_id}/status", json=lock_data, headers=headers)
    
    if response.status_code == 200:
        updated_mod = response.json()
        is_active = updated_mod.get('is_active')
        
        if not is_active:
            log_success(f"Moderator locked: is_active = {is_active}")
            return True
        else:
            log_error(f"Moderator is still active after lock attempt")
            return False
    else:
        log_error(f"Failed to lock moderator: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_unlock_moderator(headers, mod_id):
    """Test: Unlock moderator account"""
    print(f"\n{Colors.BLUE}=== Test 4: Unlock Moderator ==={Colors.END}")
    
    unlock_data = {
        "action": "unlock",
        "reason": "Testing unlock functionality"
    }
    
    log_info(f"Unlocking moderator ID: {mod_id}")
    response = requests.patch(f"{BASE_URL}/api/v1/admin/moderators/{mod_id}/status", json=unlock_data, headers=headers)
    
    if response.status_code == 200:
        updated_mod = response.json()
        is_active = updated_mod.get('is_active')
        
        if is_active:
            log_success(f"Moderator unlocked: is_active = {is_active}")
            return True
        else:
            log_error(f"Moderator is still inactive after unlock attempt")
            return False
    else:
        log_error(f"Failed to unlock moderator: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def run_all_tests():
    """Run all moderator tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Moderator API Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    # Step 1: Login
    token = login_admin()
    if not token:
        log_error("Cannot proceed without admin token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Test list moderators
    if not test_list_moderators(headers):
        log_warning("List moderators test failed, but continuing...")
    
    # Step 3: Test create moderator
    mod_id = test_create_moderator(headers)
    if not mod_id:
        log_error("Cannot proceed without created moderator")
        return False
    
    # Step 4: Test lock moderator
    if not test_lock_moderator(headers, mod_id):
        log_warning("Lock moderator test failed")
    
    # Step 5: Test unlock moderator
    if not test_unlock_moderator(headers, mod_id):
        log_warning("Unlock moderator test failed")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}All tests completed{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return True

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        log_error(f"Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
