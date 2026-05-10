from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QMessageBox,
                             QTextEdit, QComboBox, QFrame, QDateEdit,
                             QScrollArea, QGridLayout, QSizePolicy)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QPainter

class TaskCreationDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("Create Issue - Karyaradhane")
        self.setFixedSize(600, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #f4f5f7;
            }
            QFrame#main_frame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe1e6;
            }
            QLabel {
                font-size: 13px;
                color: #172b4d;
                font-weight: 500;
                margin-bottom: 4px;
            }
            QLabel#title_label {
                font-size: 18px;
                font-weight: bold;
                color: #172b4d;
                margin-bottom: 20px;
            }
            QLabel#section_label {
                font-size: 14px;
                font-weight: 600;
                color: #5e6c84;
                margin-top: 16px;
                margin-bottom: 8px;
                text-transform: uppercase;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                border: 2px solid #dfe1e6;
                border-radius: 3px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #fafbfc;
                color: #172b4d;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #0052cc;
                background-color: white;
                color: #172b4d;
                outline: none;
            }
            QPushButton {
                background-color: #0052cc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #026aa7;
            }
            QPushButton#cancel_btn {
                background-color: transparent;
                color: #5e6c84;
                border: none;
            }
            QPushButton#cancel_btn:hover {
                background-color: #ebecf0;
                color: #172b4d;
            }
        """)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # Scroll area for the form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Main content frame
        main_frame = QFrame()
        main_frame.setObjectName("main_frame")
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(32, 32, 32, 32)
        frame_layout.setSpacing(16)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        # Task type icon (simulate Jira's task icon)
        icon_label = QLabel("📋")
        icon_label.setStyleSheet("font-size: 24px; margin-right: 12px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("Create Issue")
        title_label.setObjectName("title_label")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        frame_layout.addLayout(header_layout)
        
        # Required fields section
        required_section = QLabel("Required *")
        required_section.setObjectName("section_label")
        frame_layout.addWidget(required_section)
        
        # Project field
        frame_layout.addWidget(QLabel("Project *"))
        self.project_combo = QComboBox()
        frame_layout.addWidget(self.project_combo)
        
        # Issue Type
        frame_layout.addWidget(QLabel("Issue Type *"))
        self.issue_type_combo = QComboBox()
        self.issue_type_combo.addItems(["📋 Karya", "🐛 Bug", "📈 Katha", "⚡ Purana"])
        frame_layout.addWidget(self.issue_type_combo)
        
        # Summary (Title)
        frame_layout.addWidget(QLabel("Summary *"))
        self.summary_input = QLineEdit()
        self.summary_input.setPlaceholderText("What needs to be done?")
        frame_layout.addWidget(self.summary_input)
        
        # Details section
        details_section = QLabel("Details")
        details_section.setObjectName("section_label")
        frame_layout.addWidget(details_section)
        
        # Description
        frame_layout.addWidget(QLabel("Description"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Add a description...")
        self.description_input.setMaximumHeight(120)
        frame_layout.addWidget(self.description_input)
        
        # Two column layout for fields
        details_grid = QGridLayout()
        
        # Priority
        details_grid.addWidget(QLabel("Priority"), 0, 0)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["🔴 Highest", "🟠 High", "🟡 Medium", "🟢 Low", "⚪ Lowest"])
        self.priority_combo.setCurrentIndex(2)  # Default to Medium
        details_grid.addWidget(self.priority_combo, 1, 0)
        
        # Assignee
        details_grid.addWidget(QLabel("Assignee"), 0, 1)
        self.assignee_combo = QComboBox()
        details_grid.addWidget(self.assignee_combo, 1, 1)
        
        # Labels (Status)
        details_grid.addWidget(QLabel("Status"), 2, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["📝 To Do", "🔄 In Progress", "👀 In Review", "✅ Done"])
        details_grid.addWidget(self.status_combo, 3, 0)
        
        # Due Date
        details_grid.addWidget(QLabel("Due Date"), 2, 1)
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))  # Default 1 week from now
        self.due_date_edit.setSpecialValueText("None")
        details_grid.addWidget(self.due_date_edit, 3, 1)
        
        frame_layout.addLayout(details_grid)
        
        # Additional Info section
        additional_section = QLabel("Additional Information")
        additional_section.setObjectName("section_label")
        frame_layout.addWidget(additional_section)
        
        # Reporter (auto-filled)
        frame_layout.addWidget(QLabel("Reporter"))
        self.reporter_label = QLabel("👤 Current User")
        self.reporter_label.setStyleSheet("color: #5e6c84; font-style: italic;")
        frame_layout.addWidget(self.reporter_label)
        
        frame_layout.addStretch()
        
        scroll_area.setWidget(main_frame)
        main_layout.addWidget(scroll_area)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("Create Issue")
        create_btn.clicked.connect(self.create_task)
        create_btn.setDefault(True)
        buttons_layout.addWidget(create_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def load_data(self):
        """Load projects and users data"""
        try:
            # Load projects
            projects = self.api_client.get_projects()
            if projects:
                for project in projects:
                    self.project_combo.addItem(f"📁 {project['name']}", project["id"])
            else:
                # Add default option if no projects
                self.project_combo.addItem("📁 Create new project", None)
            
            # Load users for assignee
            self.assignee_combo.addItem("Unassigned", None)
            
            # Reporter will be current logged-in user
            self.reporter_label.setText("👤 Current User")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
            self.project_combo.addItem("📁 Default Project", None)
            self.assignee_combo.addItem("Unassigned", None)
    
    def create_task(self):
        # Validate required fields
        if not self.summary_input.text().strip():
            QMessageBox.warning(self, "Missing Required Field", "Please enter a summary for the issue!")
            self.summary_input.setFocus()
            return
        
        # Parse form data
        title = self.summary_input.text().strip()
        description = self.description_input.toPlainText().strip()
        project_id = self.project_combo.currentData()
        
        # Parse priority (lowercase for API)
        priority_map = {
            "🔴 Highest": "urgent",
            "🟠 High": "high", 
            "🟡 Medium": "medium",
            "🟢 Low": "low",
            "⚪ Lowest": "low"
        }
        priority = priority_map.get(self.priority_combo.currentText(), "medium")
        
        # Parse status (lowercase for API)
        status_map = {
            "📝 To Do": "todo",
            "🔄 In Progress": "in_progress",
            "👀 In Review": "review",
            "✅ Done": "done"
        }
        status = status_map.get(self.status_combo.currentText(), "todo")
        
        # Get due date (optional) - format as ISO datetime string
        due_date = None
        if self.due_date_edit.date() > QDate.currentDate().addDays(-1):
            # Format as ISO datetime string with timezone
            due_date = self.due_date_edit.date().toString("yyyy-MM-dd") + "T12:00:00.000Z"
        
        try:
            print(f"Creating task with:")
            print(f"  Title: {title}")
            print(f"  Description: {description}")
            print(f"  Project ID: {project_id}")
            print(f"  Priority: {priority}")
            print(f"  Status: {status}")
            print(f"  Due Date: {due_date}")
            
            # Create the task
            result = self.api_client.create_task(
                title=title,
                description=description,
                project_id=project_id,
                priority=priority,
                status=status,
                due_date=due_date
            )
            
            if result:
                issue_key = f"PM-{result.get('id', '???')}"
                # Show success message first
                QMessageBox.information(
                    self, 
                    "Issue Created", 
                    f"✅ Issue {issue_key} has been created successfully!\n\n"
                    f"Summary: {title}\n"
                    f"Priority: {self.priority_combo.currentText()}\n"
                    f"Status: {self.status_combo.currentText()}"
                )
                # Then close the dialog
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "❌ Failed to create issue. Please check the console for details.")
        except Exception as e:
            print(f"Exception creating task: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"❌ Error creating issue:\n\n{str(e)}")