#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test all error cases for moderator creation
Runs automated tests for success and failure scenarios
"""

import requests
import json
import sys
from datetime import datetime
from typing import Tuple, Dict, Any

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@oldshop.com"
ADMIN_PASSWORD = "admin123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[PASS]{Colors.END} {msg}")

def log_error(msg):
    print(f"{Colors.RED}[FAIL]{Colors.END} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}[WARN]{Colors.END} {msg}")

def log_test(msg):
    print(f"{Colors.CYAN}[TEST]{Colors.END} {msg}")

def get_admin_token() -> str:
    """Get admin auth token"""
    log_info("Logging in as admin...")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if response.status_code != 200:
        log_error(f"Admin login failed: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
    
    token = response.json().get("access_token")
    log_success(f"Admin login successful")
    return token

def test_case(
    test_name: str,
    moderator_data: Dict[str, Any],
    expected_status: int,
    headers: Dict,
    should_contain: str = None,
    should_not_contain: str = None
) -> bool:
    """Test a single case"""
    log_test(test_name)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/moderators",
            json=moderator_data,
            headers=headers
        )
        
        success = response.status_code == expected_status
        
        if success:
            # Check response content if needed
            if should_contain:
                success = should_contain.lower() in response.text.lower()
            if should_not_contain and success:
                success = should_not_contain.lower() not in response.text.lower()
        
        if success:
            log_success(f"{test_name}")
        else:
            log_warning(f"Expected status {expected_status}, got {response.status_code}")
            print(f"  Response: {response.text[:200]}")
        
        return success
        
    except Exception as e:
        log_error(f"{test_name}: {str(e)}")
        return False

def run_all_tests():
    """Run all test cases"""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    timestamp = int(datetime.now().timestamp())
    
    total = 0
    passed = 0
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}MODERATOR CREATION ERROR TESTING{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    # ==================== MISSING FIELDS ====================
    print(f"\n{Colors.CYAN}--- Missing Required Fields ---{Colors.END}\n")
    
    tests = [
        ("Missing username", {
            "email": f"test{timestamp}@example.com",
            "password": "Pass123456",
            "full_name": "Test User"
        }, 400, "required"),
        
        ("Missing email", {
            "username": f"testuser{timestamp}",
            "password": "Pass123456",
            "full_name": "Test User"
        }, 400, "required"),
        
        ("Missing password", {
            "username": f"testuser{timestamp}",
            "email": f"test{timestamp}@example.com",
            "full_name": "Test User"
        }, 400, "required"),
        
        ("Missing full_name", {
            "username": f"testuser{timestamp}",
            "email": f"test{timestamp}@example.com",
            "password": "Pass123456"
        }, 400, "required"),
    ]
    
    for test_name, data, expected_status, should_contain in tests:
        total += 1
        if test_case(test_name, data, expected_status, headers, should_contain):
            passed += 1
    
    # ==================== VALIDATION ====================
    print(f"\n{Colors.CYAN}--- Field Validation ---{Colors.END}\n")
    
    tests = [
        ("Username too short (<3)", {
            "username": "ab",
            "email": f"test{timestamp}@example.com",
            "password": "Pass123456",
            "full_name": "Test User"
        }, 400, "between 3 and 50"),
        
        ("Password too short (<6)", {
            "username": f"testuser{timestamp}",
            "email": f"test{timestamp}@example.com",
            "password": "abc",
            "full_name": "Test User"
        }, 400, "at least 6 characters"),
        
        ("Invalid email format", {
            "username": f"testuser{timestamp}",
            "email": "notanemail",
            "password": "Pass123456",
            "full_name": "Test User"
        }, 400, "invalid email format"),
        
        ("Empty username string", {
            "username": "",
            "email": f"test{timestamp}@example.com",
            "password": "Pass123456",
            "full_name": "Test User"
        }, 400, "required"),
        
        ("Whitespace-only username", {
            "username": "   ",
            "email": f"test{timestamp}@example.com",
            "password": "Pass123456",
            "full_name": "Test User"
        }, 400, "between 3 and 50"),
    ]
    
    for test_name, data, expected_status, should_contain in tests:
        total += 1
        if test_case(test_name, data, expected_status, headers, should_contain):
            passed += 1
    
    # ==================== SUCCESS CASES ====================
    print(f"\n{Colors.CYAN}--- Success Cases ---{Colors.END}\n")
    
    # First success case
    timestamp1 = int(datetime.now().timestamp())
    total += 1
    test_name = "Valid moderator creation"
    moderator_data = {
        "username": f"validmod{timestamp1}",
        "email": f"validmod{timestamp1}@example.com",
        "password": "StrongPass123",
        "full_name": "Valid Moderator",
        "phone_number": "0987654321",
        "address": "123 Test St"
    }
    if test_case(test_name, moderator_data, 200, headers, should_contain=f"validmod{timestamp1}"):
        passed += 1
    
    # Second success case (without optional fields)
    timestamp2 = int(datetime.now().timestamp())
    total += 1
    test_name = "Valid moderator (no optional fields)"
    moderator_data = {
        "username": f"minimalmod{timestamp2}",
        "email": f"minimalmod{timestamp2}@example.com",
        "password": "MinPass123",
        "full_name": "Minimal Moderator"
    }
    if test_case(test_name, moderator_data, 200, headers, should_contain=f"minimalmod{timestamp2}"):
        passed += 1
    
    # ==================== DUPLICATE ERRORS ====================
    print(f"\n{Colors.CYAN}--- Duplicate Data ---{Colors.END}\n")
    
    # Create a moderator first
    timestamp3 = int(datetime.now().timestamp())
    dup_data = {
        "username": f"dupmod{timestamp3}",
        "email": f"dupmod{timestamp3}@example.com",
        "password": "DupPass123",
        "full_name": "Duplicate Test"
    }
    requests.post(f"{BASE_URL}/api/v1/admin/moderators", json=dup_data, headers=headers)
    
    # Try to create with same username
    total += 1
    if test_case("Duplicate username", {
        "username": f"dupmod{timestamp3}",
        "email": f"different{timestamp3}@example.com",
        "password": "Pass123456",
        "full_name": "Different User"
    }, 400, headers, should_contain="already exists"):
        passed += 1
    
    # Try to create with same email
    total += 1
    if test_case("Duplicate email", {
        "username": f"different{timestamp3}",
        "email": f"dupmod{timestamp3}@example.com",
        "password": "Pass123456",
        "full_name": "Different User"
    }, 400, headers, should_contain="already exists"):
        passed += 1
    
    # ==================== SUMMARY ====================
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}TEST RESULTS{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")
    
    print(f"Total Tests: {total}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.END}")
    print(f"Failed: {Colors.RED}{total - passed}{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}ALL TESTS PASSED!{Colors.END}\n")
        return True
    else:
        print(f"\n{Colors.YELLOW}SOME TESTS FAILED{Colors.END}\n")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        log_error(f"Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
