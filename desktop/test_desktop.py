# Desktop app test script
# Run this after installing Python and PySide6

import sys
import subprocess

def install_requirements():
    """Install required packages for desktop app"""
    packages = [
        "PySide6",
        "requests"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def test_imports():
    """Test if we can import PySide6"""
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        import requests
        print("✅ All required packages imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_qt_creation():
    """Test if we can create a simple Qt application"""
    try:
        from PySide6.QtWidgets import QApplication, QWidget, QLabel
        from PySide6.QtCore import Qt
        
        # Create application (don't show, just test creation)
        app = QApplication(sys.argv)
        widget = QWidget()
        label = QLabel("Test")
        widget.close()
        
        print("✅ Qt application created successfully!")
        return True
    except Exception as e:
        print(f"❌ Qt creation error: {e}")
        return False

if __name__ == "__main__":
    print("🖥️  Testing Project Management Desktop App...")
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
    
    # Test Qt creation
    if test_qt_creation():
        print()
        print("✅ Desktop app test completed successfully!")
        print()
        print("To run the desktop app:")
        print("python main.py")
    else:
        print("❌ Desktop app test failed")
        sys.exit(1)