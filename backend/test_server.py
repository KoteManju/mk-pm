#!/usr/bin/env python3
"""Test server startup to catch errors"""
import sys
import os

# Set PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    print("Importing main app...")
    from main import app
    print("✅ App imported successfully")
    
    print("Starting server...")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
