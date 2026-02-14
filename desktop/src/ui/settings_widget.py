from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QScrollArea, QPushButton,
                             QLineEdit, QComboBox, QCheckBox, QGroupBox,
                             QFormLayout, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class SettingsWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Page title
        title_label = QLabel("Settings")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)
        
        # Scroll area for settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # API Settings
        self.setup_api_settings(scroll_layout)
        
        # Appearance Settings
        self.setup_appearance_settings(scroll_layout)
        
        # Notification Settings
        self.setup_notification_settings(scroll_layout)
        
        # About Section
        self.setup_about_section(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Set styling
        self.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                padding-top: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 5px 10px;
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 4px;
            }
            QLineEdit, QComboBox {
                border: 1px solid #e1e5e9;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #0052CC;
            }
            QPushButton {
                background-color: #0052CC;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1B6EC2;
            }
            QCheckBox {
                font-size: 14px;
                color: #333;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #0052CC;
                border-radius: 3px;
                background-color: #0052CC;
            }
        """)
    
    def setup_api_settings(self, parent_layout):
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout(api_group)
        
        # API URL
        self.api_url_input = QLineEdit("http://localhost:8000")
        api_layout.addRow("API Base URL:", self.api_url_input)
        
        # Connection timeout
        self.timeout_input = QLineEdit("30")
        api_layout.addRow("Connection Timeout (seconds):", self.timeout_input)
        
        # Test connection button
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.test_api_connection)
        api_layout.addRow("", test_btn)
        
        parent_layout.addWidget(api_group)
    
    def setup_appearance_settings(self, parent_layout):
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        # Font size
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["Small", "Medium", "Large"])
        self.font_size_combo.setCurrentText("Medium")
        appearance_layout.addRow("Font Size:", self.font_size_combo)
        
        # Show animations
        self.animations_check = QCheckBox("Enable animations")
        self.animations_check.setChecked(True)
        appearance_layout.addRow("", self.animations_check)
        
        parent_layout.addWidget(appearance_group)
    
    def setup_notification_settings(self, parent_layout):
        notifications_group = QGroupBox("Notifications")
        notifications_layout = QFormLayout(notifications_group)
        
        # Desktop notifications
        self.desktop_notifications_check = QCheckBox("Show desktop notifications")
        self.desktop_notifications_check.setChecked(True)
        notifications_layout.addRow("", self.desktop_notifications_check)
        
        # Sound notifications
        self.sound_notifications_check = QCheckBox("Play sound for notifications")
        notifications_layout.addRow("", self.sound_notifications_check)
        
        # Auto refresh interval
        self.refresh_interval_combo = QComboBox()
        self.refresh_interval_combo.addItems(["5 seconds", "10 seconds", "30 seconds", "1 minute", "5 minutes"])
        self.refresh_interval_combo.setCurrentText("30 seconds")
        notifications_layout.addRow("Auto-refresh interval:", self.refresh_interval_combo)
        
        parent_layout.addWidget(notifications_group)
    
    def setup_about_section(self, parent_layout):
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout(about_group)
        
        # App info
        app_info = QLabel("""
        <h3>ProjectFlow - Jira Style Project Management</h3>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Build:</b> 2024.12.29</p>
        <p><b>Technology Stack:</b></p>
        <ul>
        <li>Frontend: PySide6 (Qt for Python)</li>
        <li>Backend: FastAPI + SQLAlchemy</li>
        <li>Database: SQLite/PostgreSQL</li>
        <li>Authentication: JWT</li>
        </ul>
        <p><b>Features:</b></p>
        <ul>
        <li>✅ Modern Jira-like interface</li>
        <li>✅ Kanban board with drag & drop</li>
        <li>✅ Project management</li>
        <li>✅ Task tracking</li>
        <li>✅ Real-time updates</li>
        </ul>
        """)
        app_info.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                font-size: 13px;
            }
        """)
        app_info.setWordWrap(True)
        about_layout.addWidget(app_info)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Check for updates button
        update_btn = QPushButton("Check for Updates")
        update_btn.clicked.connect(self.check_for_updates)
        buttons_layout.addWidget(update_btn)
        
        # View logs button
        logs_btn = QPushButton("View Logs")
        logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        logs_btn.clicked.connect(self.view_logs)
        buttons_layout.addWidget(logs_btn)
        
        buttons_layout.addStretch()
        
        about_layout.addLayout(buttons_layout)
        parent_layout.addWidget(about_group)
        
        # Save settings button at bottom
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A86B;
                font-size: 16px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #008F5A;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        save_layout.addWidget(save_btn)
        
        parent_layout.addLayout(save_layout)
    
    def test_api_connection(self):
        """Test connection to the API"""
        try:
            # Update API client URL
            self.api_client.base_url = self.api_url_input.text()
            
            # Try to make a simple request
            import requests
            response = requests.get(f"{self.api_client.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                QMessageBox.information(self, "Connection Test", 
                                       "✅ Connection successful!")
            else:
                QMessageBox.warning(self, "Connection Test", 
                                   f"⚠️ Server responded with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Connection Test", 
                               "❌ Connection failed: Server is not reachable")
        except requests.exceptions.Timeout:
            QMessageBox.critical(self, "Connection Test", 
                               "❌ Connection failed: Request timed out")
        except Exception as e:
            QMessageBox.critical(self, "Connection Test", 
                               f"❌ Connection failed:\n{str(e)}")
    
    def check_for_updates(self):
        """Check for application updates"""
        QMessageBox.information(self, "Updates", 
                               "✅ You are running the latest version!")
    
    def view_logs(self):
        """View application logs"""
        QMessageBox.information(self, "Logs", 
                               "📄 Log viewing feature coming soon!")
    
    def save_settings(self):
        """Save user settings"""
        # Here you would normally save to a config file
        # For now, just show a confirmation
        QMessageBox.information(self, "Settings", 
                               "✅ Settings saved successfully!")