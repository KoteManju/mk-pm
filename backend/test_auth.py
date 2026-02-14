#!/usr/bin/env python3
"""Test authentication directly"""
import requests

print("=" * 60)
print("Testing Authentication")
print("=" * 60)
print()

# Test 1: Login with admin credentials
print("1. Testing login with admin/admin123...")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/auth/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ SUCCESS - Token received")
        token_data = response.json()
        print(f"   Token: {token_data.get('access_token', '')[:50]}...")
    else:
        print(f"   ❌ FAILED")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 2: Try to create a user
print("2. Testing user creation...")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/users/",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "role": "member",
            "password": "newpass123"
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"   ✅ SUCCESS - User created")
    else:
        print(f"   ❌ FAILED")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("=" * 60)
