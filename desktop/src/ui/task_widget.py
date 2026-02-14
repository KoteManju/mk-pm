from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDialog, QLineEdit, QTextEdit, 
                             QLabel, QComboBox)
from PySide6.QtCore import Qt

class TaskWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with buttons
        header_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.refresh_button)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Tasks table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Title", "Status", "Priority", "Project", "Assignee"
        ])
        
        # Make table headers stretch
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
    
    def refresh_data(self):
        try:
            tasks = self.api_client.get_tasks()
            self.table.setRowCount(len(tasks))
            
            for row, task in enumerate(tasks):
                self.table.setItem(row, 0, QTableWidgetItem(str(task["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(task["title"]))
                self.table.setItem(row, 2, QTableWidgetItem(task["status"]))
                self.table.setItem(row, 3, QTableWidgetItem(task["priority"]))
                self.table.setItem(row, 4, QTableWidgetItem(str(task["project_id"])))
                assignee = str(task["assignee_id"]) if task.get("assignee_id") else "Unassigned"
                self.table.setItem(row, 5, QTableWidgetItem(assignee))
        except Exception as e:
            print(f"Error refreshing tasks: {e}")
    
    def add_task(self):
        dialog = TaskDialog(self.api_client, self)
        if dialog.exec():
            self.refresh_data()

class TaskDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        
        self.setWindowTitle("Add Task")
        self.setFixedSize(400, 350)
        self.setModal(True)
        
        self.setup_ui()
        self.load_projects()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Task title
        layout.addWidget(QLabel("Task Title:"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)
        
        # Task description
        layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addWidget(self.description_input)
        
        # Project selection
        layout.addWidget(QLabel("Project:"))
        self.project_combo = QComboBox()
        layout.addWidget(self.project_combo)
        
        # Priority
        layout.addWidget(QLabel("Priority:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high", "urgent"])
        self.priority_combo.setCurrentText("medium")
        layout.addWidget(self.priority_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_task)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def load_projects(self):
        try:
            projects = self.api_client.get_projects()
            for project in projects:
                self.project_combo.addItem(project["name"], project["id"])
        except Exception as e:
            print(f"Error loading projects: {e}")
    
    def create_task(self):
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        priority = self.priority_combo.currentText()
        project_id = self.project_combo.currentData()
        
        if not title or project_id is None:
            return
        
        result = self.api_client.create_task(title, project_id, description, priority)
        if result:
            self.accept()
        else:
            # Show error message
            pass