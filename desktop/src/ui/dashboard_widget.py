from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QGridLayout, QPushButton,
                             QScrollArea, QProgressBar)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette

class DashboardWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setup_ui()
        
        # Auto-refresh timer (re-enabled)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with title and refresh button
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Dashboard")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A86B;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #008F5A;
            }
            QPushButton:pressed {
                background-color: #007A4D;
            }
        """)
        refresh_btn.clicked.connect(self.manual_refresh)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # Stats cards row
        self.setup_stats_cards(scroll_layout)
        
        # Recent activity section
        self.setup_recent_activity(scroll_layout)
        
        # Quick actions
        self.setup_quick_actions(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Set dashboard styling
        self.setStyleSheet("""
            QFrame.stat_card {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                padding: 20px;
                margin: 5px;
            }
            QLabel.stat_number {
                font-size: 32px;
                font-weight: bold;
                color: #0052CC;
            }
            QLabel.stat_label {
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            }
            QPushButton.action_btn {
                background-color: #0052CC;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton.action_btn:hover {
                background-color: #1B6EC2;
            }
        """)
    
    def setup_stats_cards(self, parent_layout):
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        
        # Create stat cards
        self.total_projects_card = self.create_stat_card("0", "Total Projects", "#0052CC")
        self.active_tasks_card = self.create_stat_card("0", "Active Tasks", "#FF8F00")
        self.completed_tasks_card = self.create_stat_card("0", "Completed", "#00A86B")
        self.overdue_tasks_card = self.create_stat_card("0", "Overdue", "#FF4757")
        
        stats_layout.addWidget(self.total_projects_card)
        stats_layout.addWidget(self.active_tasks_card)
        stats_layout.addWidget(self.completed_tasks_card)
        stats_layout.addWidget(self.overdue_tasks_card)
        
        parent_layout.addWidget(stats_frame)
    
    def create_stat_card(self, number, label, color):
        card = QFrame()
        card.setObjectName("stat_card")
        card.setProperty("class", "stat_card")
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        number_label = QLabel(number)
        number_label.setProperty("class", "stat_number")
        number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_label.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold;")
        
        text_label = QLabel(label)
        text_label.setProperty("class", "stat_label")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("color: #666; font-size: 14px;")
        
        layout.addWidget(number_label)
        layout.addWidget(text_label)
        
        # Store label references for updating
        card.number_label = number_label
        card.text_label = text_label
        
        return card
    
    def setup_recent_activity(self, parent_layout):
        # Recent activity section
        activity_title = QLabel("Recent Activity")
        activity_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin: 10px 0;")
        parent_layout.addWidget(activity_title)
        
        self.activity_frame = QFrame()
        self.activity_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        self.activity_layout = QVBoxLayout(self.activity_frame)
        
        # Placeholder for activity items
        placeholder_label = QLabel("No recent activity")
        placeholder_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.activity_layout.addWidget(placeholder_label)
        
        parent_layout.addWidget(self.activity_frame)
    
    def setup_quick_actions(self, parent_layout):
        # Quick actions section
        actions_title = QLabel("Quick Actions")
        actions_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin: 10px 0;")
        parent_layout.addWidget(actions_title)
        
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        
        # Action buttons
        new_project_btn = QPushButton("✚ New Project")
        new_project_btn.setProperty("class", "action_btn")
        new_project_btn.clicked.connect(self.create_new_project)
        
        new_task_btn = QPushButton("📝 New Task")
        new_task_btn.setProperty("class", "action_btn")
        new_task_btn.clicked.connect(self.create_new_task)
        
        view_reports_btn = QPushButton("📊 View Reports")
        view_reports_btn.setProperty("class", "action_btn")
        view_reports_btn.clicked.connect(self.view_reports)
        
        actions_layout.addWidget(new_project_btn)
        actions_layout.addWidget(new_task_btn)
        actions_layout.addWidget(view_reports_btn)
        actions_layout.addStretch()
        
        parent_layout.addWidget(actions_frame)
    
    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            # Get projects
            projects = self.api_client.get_projects()
            total_projects = len(projects) if projects else 0
            
            # Get tasks
            tasks = self.api_client.get_tasks() 
            active_tasks = 0
            completed_tasks = 0
            
            if tasks:
                active_tasks = len([t for t in tasks if t.get("status") in ["todo", "in_progress"]])
                completed_tasks = len([t for t in tasks if t.get("status") == "done"])
            
            # Update stat cards
            self.total_projects_card.number_label.setText(str(total_projects))
            self.active_tasks_card.number_label.setText(str(active_tasks))
            self.completed_tasks_card.number_label.setText(str(completed_tasks))
            
            # For demo, set overdue to 0
            self.overdue_tasks_card.number_label.setText("0")
            
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
            # Set default values on error
            self.total_projects_card.number_label.setText("0")
            self.active_tasks_card.number_label.setText("0") 
            self.completed_tasks_card.number_label.setText("0")
            self.overdue_tasks_card.number_label.setText("0")
    
    def create_new_project(self):
        # Signal to parent to show project creation
        from .project_list import ProjectCreationDialog
        dialog = ProjectCreationDialog(self.api_client, self)
        if dialog.exec():
            try:
                self.refresh_data()
            except Exception as e:
                print(f"Error refreshing after project creation: {e}")
                # Silently fail - project was created successfully
    
    def create_new_task(self):
        # Show comprehensive task creation dialog
        from .task_dialog import TaskCreationDialog
        
        dialog = TaskCreationDialog(self.api_client, self)
        if dialog.exec():
            try:
                self.refresh_data()
            except Exception as e:
                print(f"Error refreshing after task creation: {e}")
                # Silently fail - task was created successfully
    
    def view_reports(self):
        # Placeholder for reports view
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Reports", "Reports feature coming soon!")
    
    def manual_refresh(self):
        """Manual refresh triggered by button click"""
        from PySide6.QtWidgets import QMessageBox
        try:
            self.refresh_data()
            QMessageBox.information(self, "Refreshed", "✅ Dashboard data refreshed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to refresh: {str(e)}")