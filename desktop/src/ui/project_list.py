from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QScrollArea, QPushButton,
                             QMessageBox, QDialog, QLineEdit, QTextEdit,
                             QGridLayout, QProgressBar)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette, QPixmap

class ProjectCard(QFrame):
    def __init__(self, project_data, api_client, parent_widget=None):
        super().__init__()
        self.project_data = project_data
        self.api_client = api_client
        self.parent_widget = parent_widget
        self.setup_ui()
    
    def setup_ui(self):
        self.setFrameStyle(QFrame.Shape.Box)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dfe1e6;
                border-radius: 3px;
                padding: 16px;
                margin: 5px;
            }
            QFrame:hover {
                background-color: #f4f5f7;
                border-color: #0052CC;
            }
            QLabel.project_title {
                font-weight: bold;
                font-size: 16px;
                color: #172b4d;
            }
            QLabel.project_desc {
                color: #5e6c84;
                font-size: 13px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Project title
        title_label = QLabel(self.project_data.get("name", "Untitled Project"))
        title_label.setProperty("class", "project_title")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Project description (shortened)
        desc = self.project_data.get("description", "")
        if desc:
            desc_label = QLabel(desc[:80] + "..." if len(desc) > 80 else desc)
            desc_label.setProperty("class", "project_desc")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Simple footer with ID
        footer_label = QLabel(f"ID: {self.project_data.get('id', 'N/A')}")
        footer_label.setStyleSheet("color: #a5adba; font-size: 11px;")
        layout.addWidget(footer_label)
        
        # Click handler to view project
        self.mousePressEvent = lambda e: self.view_project()
    
    def view_project(self):
        """View project tasks in Kanban board"""
        if self.parent_widget:
            project_id = self.project_data.get('id')
            project_name = self.project_data.get('name')
            self.parent_widget.view_project_tasks(project_id, project_name)

class ProjectCreationDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("Create New Project")
        self.setFixedSize(450, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f4f5f7;
            }
            QLabel {
                font-size: 13px;
                color: #172b4d;
                font-weight: 500;
            }
            QLineEdit, QTextEdit {
                border: 2px solid #dfe1e6;
                border-radius: 3px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #172b4d;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #0052CC;
                background-color: white;
                color: #172b4d;
            }
            QPushButton {
                background-color: #0052CC;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0747a6;
            }
            QPushButton#cancel_btn {
                background-color: transparent;
                color: #42526e;
                border: 1px solid #dfe1e6;
            }
            QPushButton#cancel_btn:hover {
                background-color: #ebecf0;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Create New Project")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Project name
        layout.addWidget(QLabel("Project Name *"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter project name")
        layout.addWidget(self.name_input)
        
        # Project description
        layout.addWidget(QLabel("Description"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter project description")
        self.description_input.setMaximumHeight(120)
        layout.addWidget(self.description_input)
        
        layout.addStretch()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("Create Project")
        create_btn.clicked.connect(self.create_project)
        create_btn.setDefault(True)
        buttons_layout.addWidget(create_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_project(self):
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "Project name is required!")
            return
        
        try:
            result = self.api_client.create_project(name, description)
            if result:
                # Show success message first
                QMessageBox.information(self, "Success", "✅ Project created successfully!")
                # Then close the dialog
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to create project")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating project: {str(e)}")

class ProjectListWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setup_ui()
        # Load initial data
        self.refresh_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📁 Projects")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #172b4d;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Refresh projects")
        refresh_btn.setFixedSize(36, 36)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #dfe1e6;
                border-radius: 3px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #f4f5f7;
                border-color: #0052CC;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        # Create project button
        create_btn = QPushButton("+ Create Project")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #0052CC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0747a6;
            }
        """)
        create_btn.clicked.connect(self.create_project)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Projects grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.projects_widget = QWidget()
        self.projects_layout = QGridLayout(self.projects_widget)
        self.projects_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll_area.setWidget(self.projects_widget)
        layout.addWidget(scroll_area)
        
        # Show placeholder initially
        self.show_placeholder()
    
    def show_placeholder(self):
        placeholder = QLabel("📁 No projects yet\n\nClick 'Create Project' to get started")
        placeholder.setStyleSheet("""
            color: #5e6c84;
            font-size: 14px;
            padding: 60px;
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.projects_layout.addWidget(placeholder, 0, 0, 1, 3)
    
    def clear_projects(self):
        while self.projects_layout.count():
            child = self.projects_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def refresh_data(self):
        """Refresh projects list"""
        try:
            self.clear_projects()
            
            projects = self.api_client.get_projects()
            
            if not projects:
                self.show_placeholder()
                return
            
            # Display projects in a grid (4 columns for cleaner look)
            row, col = 0, 0
            max_cols = 4
            
            for project in projects:
                project_card = ProjectCard(project, self.api_client, parent_widget=self)
                self.projects_layout.addWidget(project_card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
        except Exception as e:
            print(f"Error refreshing projects: {e}")
            self.show_placeholder()
    
    def create_project(self):
        dialog = ProjectCreationDialog(self.api_client, self)
        if dialog.exec():
            self.refresh_data()
    
    def view_project_tasks(self, project_id, project_name):
        """Switch to Kanban view filtered by project"""
        # Find the main window and switch to Kanban view with filter
        main_window = self.window()
        if hasattr(main_window, 'show_project_kanban'):
            main_window.show_project_kanban(project_id, project_name)