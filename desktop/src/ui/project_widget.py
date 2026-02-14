from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDialog, QLineEdit, QTextEdit, QLabel)
from PySide6.QtCore import Qt

class ProjectWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with buttons
        header_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Project")
        self.add_button.clicked.connect(self.add_project)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.refresh_button)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Projects table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Owner"])
        
        # Make table headers stretch
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
    
    def refresh_data(self):
        try:
            projects = self.api_client.get_projects()
            self.table.setRowCount(len(projects))
            
            for row, project in enumerate(projects):
                self.table.setItem(row, 0, QTableWidgetItem(str(project["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(project["name"]))
                self.table.setItem(row, 2, QTableWidgetItem(project.get("description", "")))
                self.table.setItem(row, 3, QTableWidgetItem(str(project["owner_id"])))
        except Exception as e:
            print(f"Error refreshing projects: {e}")
    
    def add_project(self):
        dialog = ProjectDialog(self.api_client, self)
        if dialog.exec():
            self.refresh_data()

class ProjectDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        
        self.setWindowTitle("Add Project")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Project name
        layout.addWidget(QLabel("Project Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Project description
        layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        layout.addWidget(self.description_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_project)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def create_project(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        
        if not name:
            return
        
        result = self.api_client.create_project(name, description)
        if result:
            self.accept()
        else:
            # Show error message
            pass