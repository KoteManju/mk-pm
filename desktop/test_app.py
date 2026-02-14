#!/usr/bin/env python3
"""
Simple test for the desktop application
"""

import sys
import os

def test_desktop_app():
    """Test if we can import and run the desktop app"""
    print("🖥️  Testing Project Management Desktop App...")
    print()
    
    try:
        # Test PySide6 import
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        print("✅ PySide6 imported successfully")
        
        # Test requests import
        import requests
        print("✅ Requests library imported successfully")
        
        # Test API client
        sys.path.insert(0, 'src')
        from src.api.client import APIClient
        
        api_client = APIClient()
        print("✅ API client created successfully")
        
        # Test API connection (optional)
        try:
            response = requests.get("http://localhost:8000", timeout=2)
            if response.status_code == 200:
                print("✅ Backend API is running and accessible")
            else:
                print("⚠️  Backend API responded but with unexpected status")
        except:
            print("⚠️  Backend API is not running (start it with start_backend.bat)")
        
        print()
        print("🎉 Desktop app test completed successfully!")
        print()
        print("To run the full desktop app:")
        print("   python main.py")
        print("   or")
        print("   start_desktop.bat")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_desktop_app()