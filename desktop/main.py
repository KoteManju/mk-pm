import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.api.client import APIClient
from src.config import load_settings

def main():
    app = QApplication(sys.argv)
    
    settings = load_settings()
    api_client = APIClient(base_url=settings["api_base_url"])
    
    # Create and show main window
    window = MainWindow(api_client)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()