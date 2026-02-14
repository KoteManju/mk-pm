from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QScrollArea, QPushButton,
                             QMessageBox, QDialog, QLineEdit, QTextEdit,
                             QComboBox, QListWidget, QListWidgetItem, QApplication)
from PySide6.QtCore import Qt, QMimeData, QTimer
from PySide6.QtGui import QDrag, QPixmap, QPainter, QFont

class TaskCard(QFrame):
    def __init__(self, task_data, api_client):
        super().__init__()
        self.task_data = task_data
        self.api_client = api_client
        self.setup_ui()
    
    def setup_ui(self):
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 12px;
                margin: 5px 2px;
            }
            QFrame:hover {
                border-color: #0052CC;
            }
            QLabel.task_title {
                font-weight: bold;
                font-size: 14px;
                color: #333;
                margin-bottom: 5px;
            }
            QLabel.task_desc {
                color: #666;
                font-size: 12px;
                margin-bottom: 8px;
            }
            QLabel.task_priority {
                font-size: 10px;
                padding: 2px 6px;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Task title
        title_label = QLabel(self.task_data.get("title", "Untitled"))
        title_label.setProperty("class", "task_title")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Task description
        desc = self.task_data.get("description", "")
        if desc:
            desc_label = QLabel(desc[:100] + "..." if len(desc) > 100 else desc)
            desc_label.setProperty("class", "task_desc")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Priority and assignee info
        info_layout = QHBoxLayout()
        
        # Priority badge
        priority = self.task_data.get("priority", "medium").upper()
        priority_label = QLabel(priority)
        priority_label.setProperty("class", "task_priority")
        
        priority_colors = {
            "LOW": "background-color: #00A86B; color: white;",
            "MEDIUM": "background-color: #FF8F00; color: white;",
            "HIGH": "background-color: #FF4757; color: white;",
            "URGENT": "background-color: #8B0000; color: white;"
        }
        priority_label.setStyleSheet(priority_colors.get(priority, priority_colors["MEDIUM"]))
        info_layout.addWidget(priority_label)
        
        info_layout.addStretch()
        
        # Task ID
        task_id = QLabel(f"#{self.task_data.get('id', 'N/A')}")
        task_id.setStyleSheet("color: #999; font-size: 10px;")
        info_layout.addWidget(task_id)
        
        layout.addLayout(info_layout)
        
        # Enable drag and drop
        self.setAcceptDrops(False)  # Cards don't accept drops, columns do
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
    
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if hasattr(self, 'drag_start_position'):
            if ((event.pos() - self.drag_start_position).manhattanLength() < 
                QApplication.startDragDistance()):
                return
        
        # Start drag operation
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(str(self.task_data.get("id", "")))
        mimeData.setData("application/x-taskdata", str(self.task_data.get("id", "")).encode())
        
        # Create drag pixmap
        pixmap = self.grab()
        
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        # Execute drag
        dropAction = drag.exec(Qt.DropAction.MoveAction)

class KanbanColumn(QFrame):
    def __init__(self, title, status, api_client):
        super().__init__()
        self.title = title
        self.status = status
        self.api_client = api_client
        self.tasks = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QFrame {
                background-color: #f5f6f8;
                border-radius: 8px;
                margin: 5px;
            }
            QLabel.column_title {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 15px;
                background-color: #e1e5e9;
                border-radius: 8px 8px 0 0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Column header
        header_layout = QHBoxLayout()
        title_label = QLabel(self.title)
        title_label.setProperty("class", "column_title")
        
        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("""
            background-color: #0052CC;
            color: white;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 12px;
            font-weight: bold;
            margin: 15px 15px 15px 0;
        """)
        
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #e1e5e9; border-radius: 8px 8px 0 0;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.count_label)
        
        layout.addWidget(header_frame)
        
        # Scrollable task area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.task_widget = QWidget()
        self.task_layout = QVBoxLayout(self.task_widget)
        self.task_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.task_layout.setSpacing(5)
        
        scroll_area.setWidget(self.task_widget)
        layout.addWidget(scroll_area)
    
    def add_task(self, task_data):
        task_card = TaskCard(task_data, self.api_client)
        self.task_layout.addWidget(task_card)
        self.tasks.append(task_data)
        self.update_count()
    
    def clear_tasks(self):
        # Remove all task widgets
        while self.task_layout.count():
            child = self.task_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.tasks.clear()
        self.update_count()
    
    def update_count(self):
        self.count_label.setText(str(len(self.tasks)))
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-taskdata"):
            event.accept()
            self.setStyleSheet(self.styleSheet() + "QFrame { border: 2px dashed #0052CC; }")
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("QFrame { border: 2px dashed #0052CC; }", ""))
    
    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-taskdata"):
            task_id = event.mimeData().data("application/x-taskdata").data().decode()
            self.handle_task_drop(task_id)
            event.accept()
            self.setStyleSheet(self.styleSheet().replace("QFrame { border: 2px dashed #0052CC; }", ""))
        else:
            event.ignore()
    
    def handle_task_drop(self, task_id):
        # Update task status via API
        try:
            result = self.api_client.update_task_status(int(task_id), self.status)
            if result:
                # Refresh the board
                if hasattr(self.parent().parent(), 'refresh_data'):
                    self.parent().parent().refresh_data()
            else:
                QMessageBox.warning(self, "Error", "Failed to update task status")
        except Exception as e:
            print(f"Error updating task: {e}")

class KanbanBoard(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.current_project_id = None  # For filtering by project
        self.setup_ui()
        
        # Load initial data
        self.refresh_data()
        
        # Auto-refresh timer (re-enabled)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Kanban Board")
        self.title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        """)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Project filter dropdown
        filter_label = QLabel("Filter by Project:")
        filter_label.setStyleSheet("font-size: 14px; color: #666; margin-right: 5px;")
        header_layout.addWidget(filter_label)
        
        self.project_filter_combo = QComboBox()
        self.project_filter_combo.setMinimumWidth(200)
        self.project_filter_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #dfe1e6;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #0052CC;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
        self.project_filter_combo.currentIndexChanged.connect(self.on_project_filter_changed)
        header_layout.addWidget(self.project_filter_combo)
        
        # Load projects into filter
        self.load_project_filter()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0052CC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1B6EC2;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        # Quick task button
        quick_task_btn = QPushButton("➕ Quick Task")
        quick_task_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A86B;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #008F5A;
            }
        """)
        quick_task_btn.clicked.connect(self.create_quick_task)
        header_layout.addWidget(quick_task_btn)
        
        layout.addLayout(header_layout)
        
        # Kanban columns
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(10)
        
        # Create columns for each status
        self.todo_column = KanbanColumn("📝 To Do", "todo", self.api_client)
        self.progress_column = KanbanColumn("🔄 In Progress", "in_progress", self.api_client)
        self.review_column = KanbanColumn("👀 Review", "review", self.api_client)
        self.done_column = KanbanColumn("✅ Done", "done", self.api_client)
        
        columns_layout.addWidget(self.todo_column)
        columns_layout.addWidget(self.progress_column)
        columns_layout.addWidget(self.review_column)
        columns_layout.addWidget(self.done_column)
        
        layout.addLayout(columns_layout)
    
    def refresh_data(self, project_id=None):
        """Refresh kanban board with latest tasks"""
        try:
            # Clear all columns
            self.todo_column.clear_tasks()
            self.progress_column.clear_tasks()
            self.review_column.clear_tasks()
            self.done_column.clear_tasks()
            
            # Get tasks from API (optionally filtered by project)
            if project_id is not None:
                self.current_project_id = project_id
            tasks = self.api_client.get_tasks(project_id=self.current_project_id)
            
            # Distribute tasks to columns based on status
            for task in tasks:
                status = task.get("status", "todo")
                if status == "todo":
                    self.todo_column.add_task(task)
                elif status == "in_progress":
                    self.progress_column.add_task(task)
                elif status == "review":
                    self.review_column.add_task(task)
                elif status == "done":
                    self.done_column.add_task(task)
                    
        except Exception as e:
            print(f"Error refreshing kanban board: {e}")
    
    def load_project_filter(self):
        """Load projects into filter dropdown"""
        try:
            # Block signals to prevent triggering filter during loading
            self.project_filter_combo.blockSignals(True)
            self.project_filter_combo.clear()
            
            # Add "All Projects" option
            self.project_filter_combo.addItem("📋 All Projects", None)
            
            # Load projects from API
            projects = self.api_client.get_projects()
            for project in projects:
                project_name = project.get("name", "Untitled")
                project_id = project.get("id")
                self.project_filter_combo.addItem(f"📁 {project_name}", project_id)
            
            # Restore signals
            self.project_filter_combo.blockSignals(False)
            
        except Exception as e:
            print(f"Error loading project filter: {e}")
    
    def on_project_filter_changed(self, index):
        """Handle project filter selection change"""
        if index >= 0:
            project_id = self.project_filter_combo.itemData(index)
            project_name = self.project_filter_combo.itemText(index)
            
            if project_id is None:
                # "All Projects" selected
                self.clear_project_filter()
            else:
                # Specific project selected
                self.filter_by_project(project_id, project_name.replace("📁 ", ""))
    
    def filter_by_project(self, project_id, project_name):
        """Filter kanban board to show only tasks from a specific project"""
        self.current_project_id = project_id
        # Update combo box to show selected project (block signals to prevent recursion)
        self.project_filter_combo.blockSignals(True)
        for i in range(self.project_filter_combo.count()):
            if self.project_filter_combo.itemData(i) == project_id:
                self.project_filter_combo.setCurrentIndex(i)
                break
        self.project_filter_combo.blockSignals(False)
        self.refresh_data()
    
    def clear_project_filter(self):
        """Clear project filter and show all tasks"""
        self.current_project_id = None
        # Set combo box back to "All Projects"
        self.project_filter_combo.blockSignals(True)
        self.project_filter_combo.setCurrentIndex(0)
        self.project_filter_combo.blockSignals(False)
        self.refresh_data()
    
    def create_quick_task(self):
        """Quick task creation with minimal input"""
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        
        title, ok = QInputDialog.getText(self, 'Quick Task', 'What needs to be done?')
        
        if ok and title.strip():
            try:
                result = self.api_client.create_task(
                    title=title.strip(),
                    description="",
                    project_id=None,
                    priority="medium",
                    status="todo"
                )
                if result:
                    QMessageBox.information(self, "Success", f"✅ Task '{title}' added to To Do!")
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "Error", "Failed to create task")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
        elif ok:
            QMessageBox.warning(self, "Error", "Please enter a task title!")