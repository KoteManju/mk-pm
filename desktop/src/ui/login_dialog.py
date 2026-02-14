from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        
        self.setWindowTitle("Login")
        self.setFixedSize(300, 150)
        self.setModal(True)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Set enter key to trigger login
        self.password_input.returnPressed.connect(self.login)
        self.username_input.returnPressed.connect(self.login)
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        print(f"Login dialog: Attempting login for user: {username}")
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        try:
            print(f"Calling API client login...")
            if self.api_client.login(username, password):
                print("Login successful!")
                self.accept()  # Close dialog with success
            else:
                print("Login failed - invalid credentials")
                QMessageBox.critical(self, "Login Failed", "Invalid username or password")
                self.password_input.clear()
        except Exception as e:
            print(f"Login exception: {str(e)}")
            QMessageBox.critical(self, "Error", f"Login error: {str(e)}")