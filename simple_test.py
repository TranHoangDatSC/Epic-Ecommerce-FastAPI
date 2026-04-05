#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple test to create moderator"""

import sys
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Login as admin
login_data = {"username": "admin@oldshop.com", "password": "admin123"}
response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)

if response.status_code != 200:
    print(f"Login failed: {response.status_code}")
    print(f"Response: {response.text}")
    sys.exit(1)

token = response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Create moderator
timestamp = int(datetime.now().timestamp())
mod_data = {
    "username": f"testmod{timestamp}",
    "email": f"testmod{timestamp}@oldshop.com",
    "password": "Pass123456",
    "full_name": "Test Moderator"
}

print(f"Creating moderator: {mod_data['username']}")
response = requests.post(f"{BASE_URL}/api/v1/admin/moderators", json=mod_data, headers=headers)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code != 200:
    sys.exit(1)
