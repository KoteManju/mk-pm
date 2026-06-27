from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QGridLayout, QPushButton,
                             QScrollArea, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette, QCursor
from datetime import datetime


class ActivityRow(QFrame):
    BASE_STYLE = """
        QFrame {
            background-color: #f8f9fa;
            border-radius: 6px;
            padding: 10px;
        }
    """
    HOVER_STYLE = """
        QFrame {
            background-color: #e9f2ff;
            border: 1px solid #0052CC;
            border-radius: 6px;
            padding: 10px;
        }
    """

    def __init__(self, event, on_click, parent=None):
        super().__init__(parent)
        self.activity_data = event
        self.on_click = on_click
        self._clickable = bool(event.get("task_id") or event.get("project_id"))
        if self._clickable:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        icon_label = QLabel(event["icon"])
        icon_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        message_label = QLabel(event["text"])
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #172b4d; font-size: 13px;")
        time_label = QLabel(event.get("time_label", ""))
        time_label.setStyleSheet("color: #6b778c; font-size: 11px;")
        text_layout.addWidget(message_label)
        text_layout.addWidget(time_label)
        layout.addLayout(text_layout, 1)

        self.setStyleSheet(self.BASE_STYLE)

    def mousePressEvent(self, event):
        if (
            self._clickable
            and event.button() == Qt.MouseButton.LeftButton
            and self.on_click
        ):
            activity_data = dict(self.activity_data)
            handler = self.on_click
            QTimer.singleShot(0, lambda: handler(activity_data))
            event.accept()
            return
        super().mousePressEvent(event)

    def enterEvent(self, event):
        if self._clickable:
            self.setStyleSheet(self.HOVER_STYLE)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.BASE_STYLE)
        super().leaveEvent(event)


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
        
        title_label = QLabel("📊 Karyaradhane Dashboard")
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: 700;
            color: #172b4d;
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
        self.activity_layout.setSpacing(10)

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
            projects = self.api_client.get_projects()
            total_projects = len(projects) if projects else 0

            tasks = self.api_client.get_tasks()
            active_tasks = 0
            completed_tasks = 0

            if tasks:
                active_tasks = len([t for t in tasks if t.get("status") in ["todo", "in_progress"]])
                completed_tasks = len([t for t in tasks if t.get("status") == "done"])

            self.total_projects_card.number_label.setText(str(total_projects))
            self.active_tasks_card.number_label.setText(str(active_tasks))
            self.completed_tasks_card.number_label.setText(str(completed_tasks))
            self.overdue_tasks_card.number_label.setText("0")

            self.update_recent_activity(projects, tasks)

        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
            self.total_projects_card.number_label.setText("0")
            self.active_tasks_card.number_label.setText("0")
            self.completed_tasks_card.number_label.setText("0")
            self.overdue_tasks_card.number_label.setText("0")
            self.update_recent_activity([], [])

    def _clear_activity_layout(self):
        while self.activity_layout.count():
            item = self.activity_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _format_activity_time(self, iso_str):
        if not iso_str:
            return ""
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return dt.strftime("%b %d, %Y %I:%M %p")
        except (ValueError, TypeError):
            return str(iso_str)[:16]

    def _status_label(self, status):
        return (status or "todo").replace("_", " ").title()

    def _handle_activity_click(self, event):
        task_id = event.get("task_id")
        project_id = event.get("project_id")
        project_name = event.get("project_name") or "Project"

        try:
            if task_id:
                from .task_detail_dialog import TaskDetailDialog
                dialog = TaskDetailDialog(self.api_client, int(task_id), self)
                if dialog.exec():
                    self.refresh_data()
                return

            if project_id:
                main_window = self.window()
                if hasattr(main_window, "show_project_kanban"):
                    main_window.show_project_kanban(project_id, project_name)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not open activity item:\n{exc}")

    def update_recent_activity(self, projects, tasks):
        self._clear_activity_layout()
        events = []

        for project in projects or []:
            if project.get("created_at"):
                events.append({
                    "timestamp": project["created_at"],
                    "text": f"Project created: {project.get('name', 'Untitled')}",
                    "icon": "📁",
                    "project_id": project.get("id"),
                    "project_name": project.get("name", "Project"),
                })

        for task in tasks or []:
            task_id = task.get("id")
            title = task.get("title", "Untitled")
            created_at = task.get("created_at")
            updated_at = task.get("updated_at")
            status = self._status_label(task.get("status"))
            project_id = task.get("project_id")

            if created_at:
                events.append({
                    "timestamp": created_at,
                    "text": f"Task created: PM-{task_id} {title}",
                    "icon": "📝",
                    "task_id": task_id,
                    "project_id": project_id,
                })

            if updated_at and updated_at != created_at:
                events.append({
                    "timestamp": updated_at,
                    "text": f"Task updated: PM-{task_id} {title} → {status}",
                    "icon": "🔄",
                    "task_id": task_id,
                    "project_id": project_id,
                })

        recent_tasks = sorted(
            tasks or [],
            key=lambda item: item.get("updated_at") or item.get("created_at") or "",
            reverse=True,
        )[:8]
        for task in recent_tasks:
            comments = self.api_client.get_task_comments(task["id"])
            for comment in comments:
                author_info = comment.get("author") or {}
                author = author_info.get("full_name") or author_info.get("username") or "Someone"
                body = (comment.get("body") or "").strip()
                attachments = comment.get("attachments") or []
                if not body and attachments:
                    body = f"[{len(attachments)} attachment(s)]"
                elif len(body) > 80:
                    body = body[:77] + "..."
                events.append({
                    "timestamp": comment.get("created_at"),
                    "text": f"{author} commented on PM-{task['id']}: {body or '(comment)'}",
                    "icon": "💬",
                    "task_id": task["id"],
                    "project_id": task.get("project_id"),
                })

        events = [event for event in events if event.get("timestamp")]
        events.sort(key=lambda item: item["timestamp"], reverse=True)
        events = events[:5]

        if not events:
            placeholder = QLabel("No recent activity")
            placeholder.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.activity_layout.addWidget(placeholder)
            return

        for event in events:
            event["time_label"] = self._format_activity_time(event["timestamp"])
            self.activity_layout.addWidget(
                ActivityRow(event, self._handle_activity_click, self)
            )
    
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