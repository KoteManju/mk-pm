from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QWidget, QTabWidget, QMessageBox,
                             QSplitter, QListWidget, QListWidgetItem, QStackedWidget,
                             QLabel, QFrame, QScrollArea)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon
from .login_dialog import LoginDialog
from .dashboard_widget import DashboardWidget
from .kanban_board import KanbanBoard
from .project_list import ProjectListWidget
from .settings_widget import SettingsWidget

class MainWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.logged_in = False
        
        self.setWindowTitle("Project Management - Jira Style")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QFrame#sidebar {
                background-color: #0052CC;
                border: none;
            }
            QListWidget#sidebar_menu {
                background-color: #0052CC;
                border: none;
                color: white;
                font-size: 14px;
                padding: 10px;
            }
            QListWidget#sidebar_menu::item {
                padding: 12px 16px;
                margin: 2px 0px;
                border-radius: 4px;
            }
            QListWidget#sidebar_menu::item:selected {
                background-color: #1B6EC2;
            }
            QListWidget#sidebar_menu::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QLabel#title_label {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 20px 16px 10px 16px;
            }
            QPushButton#logout_btn {
                background-color: #FF4757;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton#logout_btn:hover {
                background-color: #FF3742;
            }
        """)
        
        self.setup_ui()
        self.show_login()
    
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_splitter)
        
        # Sidebar
        self.setup_sidebar(main_splitter)
        
        # Main content area
        self.setup_content_area(main_splitter)
        
        # Set splitter proportions
        main_splitter.setSizes([250, 1150])
        main_splitter.setCollapsible(0, False)
        
        # Initially show login state
        self.set_logged_out_state()
    
    def setup_sidebar(self, parent):
        # Sidebar frame
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Title
        title_label = QLabel("ProjectFlow")
        title_label.setObjectName("title_label")
        sidebar_layout.addWidget(title_label)
        
        # Navigation menu
        self.sidebar_menu = QListWidget()
        self.sidebar_menu.setObjectName("sidebar_menu")
        
        menu_items = [
            ("🏠 Dashboard", "dashboard"),
            ("📋 Projects", "projects"),
            ("📊 Kanban Board", "kanban"),
            ("⚙️ Settings", "settings")
        ]
        
        for text, data in menu_items:
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.sidebar_menu.addItem(item)
        
        self.sidebar_menu.currentItemChanged.connect(self.on_menu_changed)
        sidebar_layout.addWidget(self.sidebar_menu)
        
        # Spacer
        sidebar_layout.addStretch()
        
        # User info and logout
        self.user_info_label = QLabel("Not logged in")
        self.user_info_label.setStyleSheet("color: white; padding: 10px 16px; font-size: 12px;")
        sidebar_layout.addWidget(self.user_info_label)
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.setObjectName("logout_btn")
        self.logout_button.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.logout_button)
        
        parent.addWidget(sidebar)
    
    def setup_content_area(self, parent):
        # Content area with stacked widget
        self.content_stack = QStackedWidget()
        
        # Dashboard
        self.dashboard_widget = DashboardWidget(self.api_client)
        self.content_stack.addWidget(self.dashboard_widget)
        
        # Projects
        self.project_widget = ProjectListWidget(self.api_client)
        self.content_stack.addWidget(self.project_widget)
        
        # Kanban Board
        self.kanban_widget = KanbanBoard(self.api_client)
        self.content_stack.addWidget(self.kanban_widget)
        
        # Settings
        self.settings_widget = SettingsWidget(self.api_client)
        self.content_stack.addWidget(self.settings_widget)
        
        parent.addWidget(self.content_stack)
    
    def on_menu_changed(self, current, previous):
        if current:
            page = current.data(Qt.ItemDataRole.UserRole)
            if page == "dashboard":
                self.content_stack.setCurrentWidget(self.dashboard_widget)
            elif page == "projects":
                self.content_stack.setCurrentWidget(self.project_widget)
            elif page == "kanban":
                self.content_stack.setCurrentWidget(self.kanban_widget)
            elif page == "settings":
                self.content_stack.setCurrentWidget(self.settings_widget)
    
    def set_logged_out_state(self):
        self.sidebar_menu.setEnabled(False)
        self.logout_button.hide()
        self.user_info_label.setText("Please log in")
    
    def set_logged_in_state(self, username):
        self.sidebar_menu.setEnabled(True)
        self.logout_button.show()
        self.user_info_label.setText(f"Logged in as: {username}")
        self.sidebar_menu.setCurrentRow(0)  # Select dashboard
    
    def show_login(self):
        if not self.logged_in:
            login_dialog = LoginDialog(self.api_client, self)
            if login_dialog.exec():
                self.login_success()
    
    def login_success(self):
        self.logged_in = True
        self.set_logged_in_state("admin")  # You can get actual username from API
        
        # Refresh data in all widgets
        self.dashboard_widget.refresh_data()
        self.project_widget.refresh_data()
        self.kanban_widget.refresh_data()
        
        QMessageBox.information(self, "Success", "Login successful!")
    
    def logout(self):
        self.logged_in = False
        self.api_client.token = None
        self.set_logged_out_state()
        
        QMessageBox.information(self, "Logout", "Logged out successfully!")
    
    def show_project_kanban(self, project_id, project_name):
        """Switch to Kanban board and filter by project"""
        # Switch to Kanban view
        self.sidebar_menu.setCurrentRow(2)  # Kanban is index 2
        self.content_stack.setCurrentWidget(self.kanban_widget)
        
        # Filter by project
        self.kanban_widget.filter_by_project(project_id, project_name)