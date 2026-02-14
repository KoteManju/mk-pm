import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.api.client import APIClient

def main():
    app = QApplication(sys.argv)
    
    # Initialize API client
    api_client = APIClient()
    
    # Create and show main window
    window = MainWindow(api_client)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()