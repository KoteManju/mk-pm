#!/usr/bin/env python3
"""Test login functionality"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models import User
from app.core.security import verify_password, get_password_hash

# Test database connection
db = SessionLocal()
try:
    # Get admin user
    admin = db.query(User).filter(User.username == "admin").first()
    
    if admin:
        print(f"✅ Admin user found:")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Hashed password: {admin.hashed_password[:50]}...")
        
        # Test password verification
        test_password = "admin123"
        is_valid = verify_password(test_password, admin.hashed_password)
        print(f"\n🔐 Password verification test:")
        print(f"   Testing password: {test_password}")
        print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        # Generate fresh hash for comparison
        fresh_hash = get_password_hash(test_password)
        print(f"\n🔄 Fresh hash for '{test_password}':")
        print(f"   {fresh_hash[:50]}...")
        
    else:
        print("❌ Admin user NOT FOUND in database!")
        print("\n📋 All users in database:")
        users = db.query(User).all()
        for user in users:
            print(f"   - {user.username} ({user.email})")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
