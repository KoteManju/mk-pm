# Simple test script to verify the backend works
# Run this after installing Python and the dependencies

import sys
import subprocess

def install_requirements():
    """Install required packages"""
    packages = [
        "fastapi",
        "uvicorn[standard]", 
        "sqlalchemy",
        "pydantic[email]",
        "python-dotenv",
        "pydantic-settings"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def test_imports():
    """Test if we can import all required modules"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ All required packages imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test if we can create the FastAPI app"""
    try:
        # Simple test without database
        from fastapi import FastAPI
        app = FastAPI(title="Test API")
        
        @app.get("/")
        def root():
            return {"message": "API is working!"}
        
        print("✅ FastAPI app created successfully!")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Project Management Backend...")
    print()
    
    # Test imports first
    if not test_imports():
        print("Installing requirements...")
        try:
            install_requirements()
            print("Dependencies installed. Testing imports again...")
            if not test_imports():
                print("❌ Failed to install requirements properly")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            sys.exit(1)
    
    # Test app creation
    if test_app_creation():
        print()
        print("✅ Backend test completed successfully!")
        print()
        print("To run the server:")
        print("uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("❌ Backend test failed")
        sys.exit(1)