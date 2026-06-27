from datetime import datetime, timezone
from typing import List
import os

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QTextEdit, QComboBox, QFrame, QSplitter, QScrollArea, QWidget, QLineEdit,
    QFileDialog, QDateEdit,
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QPixmap, QCursor


AVATAR_COLORS = [
    "#0052CC", "#5243AA", "#00875A", "#FF5630",
    "#FF991F", "#00B8D9", "#6554C0", "#36B37E",
]

NO_DUE_DATE = QDate(2000, 1, 1)


def _initials(name: str, username: str = "") -> str:
    source = (name or username or "?").strip()
    parts = source.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return source[:2].upper()


def _avatar_color(user_id: int) -> str:
    return AVATAR_COLORS[user_id % len(AVATAR_COLORS)]


def _format_time_of_day(dt: datetime) -> str:
    return dt.strftime("%I:%M %p").lstrip("0").replace("  ", " ")


REPLY_MARKERS = (
    "-----original message-----",
    "----- forwarded message -----",
    "________________________________",
    "from:",
    "sent from my iphone",
    "sent from my android",
)


def _strip_email_quotes(text: str) -> str:
    """Trim quoted reply chains so email comments stay readable in the feed."""
    if not text:
        return ""

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cleaned: List[str] = []

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        if stripped.startswith(">"):
            break

        if " wrote:" in lower and lower.startswith("on "):
            break

        if any(marker in lower for marker in REPLY_MARKERS):
            break

        cleaned.append(line)

    return "\n".join(cleaned).strip()


def _format_jira_time(timestamp: str) -> str:
    if not timestamp:
        return ""

    try:
        normalized = timestamp.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - dt.astimezone(timezone.utc)

        if delta.days == 0:
            hours = delta.seconds // 3600
            if hours == 0:
                minutes = max(delta.seconds // 60, 1)
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        if delta.days == 1:
            return f"Yesterday at {_format_time_of_day(dt)}"
        if delta.days < 7:
            return f"{dt.strftime('%A')} at {_format_time_of_day(dt)}"
        return dt.strftime("%d %b %Y at %I:%M %p").lstrip("0")
    except ValueError:
        return timestamp.replace("T", " ")[:16]


class AvatarLabel(QLabel):
    """Circular Jira-style user avatar with initials."""

    def __init__(self, name: str, user_id: int, username: str = "", size: int = 32, parent=None):
        super().__init__(_initials(name, username), parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {_avatar_color(user_id)};
                color: white;
                border-radius: {size // 2}px;
                font-size: {max(size // 3, 10)}px;
                font-weight: 700;
            }}
            """
        )


class ClickableImageLabel(QFrame):
    """Image thumbnail with reliable click/double-click to open full size."""

    def __init__(
        self,
        full_pixmap: QPixmap,
        filename: str,
        max_width: int = 320,
        max_height: int = 240,
        parent=None,
    ):
        super().__init__(parent)
        self.full_pixmap = full_pixmap
        self.filename = filename or "Image"

        thumbnail = full_pixmap.scaled(
            max_width,
            max_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setToolTip(f"{self.filename}\nClick or double-click to view full size")
        self.setStyleSheet(
            "ClickableImageLabel, QFrame#attachment_preview {"
            "  background: #fafbfc;"
            "  border: 1px solid #dfe1e6;"
            "  border-radius: 6px;"
            "}"
            "ClickableImageLabel:hover, QFrame#attachment_preview:hover {"
            "  border-color: #4c9aff;"
            "  background: #f0f6ff;"
            "}"
        )
        self.setObjectName("attachment_preview")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.image_label = QLabel()
        self.image_label.setPixmap(thumbnail)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.image_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(self.image_label)

        view_btn = QPushButton("View full image")
        view_btn.setObjectName("ghost_btn")
        view_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        view_btn.clicked.connect(self.open_viewer)
        layout.addWidget(view_btn, alignment=Qt.AlignmentFlag.AlignLeft)

    def open_viewer(self):
        parent = self.window()
        dialog = QDialog(parent)
        dialog.setWindowTitle(self.filename)
        dialog.resize(900, 700)
        if parent:
            dialog.setStyleSheet(parent.styleSheet())

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setPixmap(self.full_pixmap)
        scroll.setWidget(image_label)
        layout.addWidget(scroll, stretch=1)

        actions = QHBoxLayout()
        actions.addStretch()

        open_btn = QPushButton("Open in viewer")
        open_btn.setObjectName("primary_btn")
        open_btn.clicked.connect(lambda: _open_pixmap_in_viewer(self.full_pixmap, self.filename))
        actions.addWidget(open_btn)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("ghost_btn")
        close_btn.clicked.connect(dialog.accept)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

        dialog.exec()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_viewer()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_viewer()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


def _open_pixmap_in_viewer(pixmap: QPixmap, filename: str) -> None:
    safe_name = os.path.basename(filename) or "attachment.png"
    temp_path = os.path.join(os.environ.get("TEMP", "."), safe_name)
    if pixmap.save(temp_path):
        os.startfile(temp_path)


class TaskDetailDialog(QDialog):
    """Jira-style issue view with Activity comments."""

    def __init__(self, api_client, task_id: int, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.task_id = task_id
        self.task_data = None
        self.users = []
        self.assignee_emails_list: List[str] = []
        self.pending_attachment_paths: List[str] = []
        self.last_comment_signature = None

        self.setWindowTitle(f"PM-{task_id}")
        self.setMinimumSize(980, 760)
        self.setStyleSheet("""
            QDialog { background-color: #f4f5f7; }
            QFrame#panel, QFrame#composer {
                background-color: #ffffff;
                border: 1px solid #dfe1e6;
                border-radius: 3px;
            }
            QFrame#comment_row {
                background-color: #ffffff;
                border: 1px solid #ebecf0;
                border-radius: 6px;
            }
            QLabel#issue_key {
                background-color: #dfe1e6;
                color: #42526e;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#issue_title {
                font-size: 22px;
                font-weight: 500;
                color: #172b4d;
            }
            QLabel#section_title {
                font-size: 12px;
                font-weight: 700;
                color: #44546f;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QLabel#sidebar_label {
                font-size: 12px;
                font-weight: 600;
                color: #626f86;
                margin-top: 8px;
            }
            QLabel#badge {
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: 700;
            }
            QTextEdit, QComboBox, QListWidget {
                border: 2px solid #dfe1e6;
                border-radius: 3px;
                padding: 8px;
                background-color: #ffffff;
                color: #172b4d;
                font-size: 14px;
            }
            QTextEdit:focus, QComboBox:focus, QListWidget:focus {
                border-color: #4c9aff;
            }
            QPushButton#primary_btn {
                background-color: #0052cc;
                color: white;
                border: none;
                padding: 6px 14px;
                border-radius: 3px;
                font-weight: 600;
            }
            QPushButton#primary_btn:hover { background-color: #0065ff; }
            QPushButton#primary_btn:disabled {
                background-color: #091e420a;
                color: #a5adba;
            }
            QPushButton#ghost_btn {
                background-color: transparent;
                color: #44546f;
                border: none;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton#ghost_btn:hover { background-color: #091e420f; border-radius: 3px; }
        """)

        self.setup_ui()
        self.load_task()
        self.load_comments()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_comments)
        self.refresh_timer.start(5000)

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        header = QHBoxLayout()
        self.issue_key_label = QLabel(f"PM-{self.task_id}")
        self.issue_key_label.setObjectName("issue_key")
        header.addWidget(self.issue_key_label)

        self.title_label = QLabel("Loading...")
        self.title_label.setObjectName("issue_title")
        self.title_label.setWordWrap(True)
        header.addWidget(self.title_label, stretch=1)

        self.status_badge = QLabel("TO DO")
        self.status_badge.setObjectName("badge")
        header.addWidget(self.status_badge)

        self.priority_badge = QLabel("MEDIUM")
        self.priority_badge.setObjectName("badge")
        header.addWidget(self.priority_badge)
        root.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        main_panel = QFrame()
        main_panel.setObjectName("panel")
        main_layout = QVBoxLayout(main_panel)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        desc_title = QLabel("Description")
        desc_title.setObjectName("section_title")
        main_layout.addWidget(desc_title)

        self.description_view = QTextEdit()
        self.description_view.setReadOnly(True)
        self.description_view.setMaximumHeight(72)
        self.description_view.setPlaceholderText("Add a description...")
        self.description_view.setStyleSheet(
            "QTextEdit { background-color: #fafbfc; font-size: 13px; }"
        )
        main_layout.addWidget(self.description_view)

        activity_header = QHBoxLayout()
        activity_header.setContentsMargins(0, 4, 0, 0)
        activity_title = QLabel("Activity")
        activity_title.setObjectName("section_title")
        activity_header.addWidget(activity_title)

        self.comments_tab = QLabel("Comments")
        self.comments_tab.setStyleSheet(
            "color: #0052cc; font-weight: 700; font-size: 12px; "
            "border-bottom: 2px solid #0052cc; padding-bottom: 4px; margin-left: 12px;"
        )
        activity_header.addWidget(self.comments_tab)
        activity_header.addStretch()

        export_pdf_btn = QPushButton("Export PDF")
        export_pdf_btn.setObjectName("ghost_btn")
        export_pdf_btn.clicked.connect(self.export_chat_pdf)
        activity_header.addWidget(export_pdf_btn)

        export_doc_btn = QPushButton("Export Word")
        export_doc_btn.setObjectName("ghost_btn")
        export_doc_btn.clicked.connect(self.export_chat_docx)
        activity_header.addWidget(export_doc_btn)

        self.comment_count_label = QLabel("0")
        self.comment_count_label.setStyleSheet("color: #626f86; font-size: 12px;")
        activity_header.addWidget(self.comment_count_label)
        main_layout.addLayout(activity_header)

        self.activity_scroll = QScrollArea()
        self.activity_scroll.setWidgetResizable(True)
        self.activity_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.activity_scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )

        self.activity_container = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.activity_layout.setContentsMargins(0, 8, 4, 8)
        self.activity_layout.setSpacing(12)
        self.activity_scroll.setWidget(self.activity_container)
        main_layout.addWidget(self.activity_scroll, stretch=1)

        self.composer_frame = QFrame()
        self.composer_frame.setObjectName("composer")
        composer_layout = QHBoxLayout(self.composer_frame)
        composer_layout.setContentsMargins(16, 14, 16, 14)
        composer_layout.setSpacing(14)

        self.composer_avatar_host = QWidget()
        self.composer_avatar_layout = QVBoxLayout(self.composer_avatar_host)
        self.composer_avatar_layout.setContentsMargins(0, 0, 0, 0)
        composer_layout.addWidget(self.composer_avatar_host, alignment=Qt.AlignmentFlag.AlignTop)

        composer_body = QVBoxLayout()
        composer_body.setSpacing(10)
        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Add a comment...")
        self.comment_input.setMinimumHeight(64)
        self.comment_input.setMaximumHeight(96)
        self.comment_input.textChanged.connect(self._update_save_button)
        composer_body.addWidget(self.comment_input)

        attach_row = QHBoxLayout()
        self.attach_btn = QPushButton("Attach image")
        self.attach_btn.setObjectName("ghost_btn")
        self.attach_btn.clicked.connect(self.attach_images)
        attach_row.addWidget(self.attach_btn)
        self.pending_attachments_label = QLabel("")
        self.pending_attachments_label.setStyleSheet("color: #626f86; font-size: 11px;")
        attach_row.addWidget(self.pending_attachments_label, stretch=1)
        composer_body.addLayout(attach_row)

        composer_actions = QHBoxLayout()
        composer_actions.addStretch()
        self.cancel_comment_btn = QPushButton("Cancel")
        self.cancel_comment_btn.setObjectName("ghost_btn")
        self.cancel_comment_btn.clicked.connect(self._clear_comment_input)
        composer_actions.addWidget(self.cancel_comment_btn)

        self.save_comment_btn = QPushButton("Save")
        self.save_comment_btn.setObjectName("primary_btn")
        self.save_comment_btn.setEnabled(False)
        self.save_comment_btn.clicked.connect(self.send_message)
        composer_actions.addWidget(self.save_comment_btn)
        composer_body.addLayout(composer_actions)
        composer_layout.addLayout(composer_body, stretch=1)
        main_layout.addWidget(self.composer_frame)

        splitter.addWidget(main_panel)

        sidebar = QFrame()
        sidebar.setObjectName("panel")
        sidebar.setMinimumWidth(300)
        sidebar.setMaximumWidth(340)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(6)

        details_title = QLabel("Details")
        details_title.setObjectName("section_title")
        sidebar_layout.addWidget(details_title)

        sidebar_layout.addWidget(self._sidebar_label("Status"))
        self.status_combo = QComboBox()
        for value, label in [
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("review", "In Review"),
            ("done", "Done"),
        ]:
            self.status_combo.addItem(label, value)
        sidebar_layout.addWidget(self.status_combo)

        sidebar_layout.addWidget(self._sidebar_label("Priority"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high", "urgent"])
        sidebar_layout.addWidget(self.priority_combo)

        sidebar_layout.addWidget(self._sidebar_label("Due date"))
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setMinimumDate(NO_DUE_DATE)
        self.due_date_edit.setSpecialValueText("None")
        self.due_date_edit.setDate(NO_DUE_DATE)
        sidebar_layout.addWidget(self.due_date_edit)

        sidebar_layout.addWidget(self._sidebar_label("Assignees"))
        self.assignee_count_label = QLabel("0 assignees")
        self.assignee_count_label.setStyleSheet("color: #626f86; font-size: 11px;")
        sidebar_layout.addWidget(self.assignee_count_label)

        self.assignee_list_scroll = QScrollArea()
        self.assignee_list_scroll.setWidgetResizable(True)
        self.assignee_list_scroll.setMaximumHeight(140)
        self.assignee_list_scroll.setStyleSheet("QScrollArea { border: 1px solid #dfe1e6; border-radius: 3px; background: #fafbfc; }")
        self.assignee_list_container = QWidget()
        self.assignee_list_layout = QVBoxLayout(self.assignee_list_container)
        self.assignee_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.assignee_list_layout.setSpacing(4)
        self.assignee_list_scroll.setWidget(self.assignee_list_container)
        sidebar_layout.addWidget(self.assignee_list_scroll)

        add_row = QHBoxLayout()
        self.add_assignee_input = QLineEdit()
        self.add_assignee_input.setPlaceholderText("Add email address")
        self.add_assignee_input.returnPressed.connect(self.add_assignee_email)
        add_row.addWidget(self.add_assignee_input)

        add_btn = QPushButton("Add")
        add_btn.setObjectName("primary_btn")
        add_btn.clicked.connect(self.add_assignee_email)
        add_row.addWidget(add_btn)
        sidebar_layout.addLayout(add_row)

        email_hint = QLabel("Add as many assignees as needed. Each gets an email notification.")
        email_hint.setWordWrap(True)
        email_hint.setStyleSheet("color: #626f86; font-size: 11px;")
        sidebar_layout.addWidget(email_hint)

        save_assignees_btn = QPushButton("Save assignees")
        save_assignees_btn.setObjectName("primary_btn")
        save_assignees_btn.clicked.connect(self.save_assignees)
        sidebar_layout.addWidget(save_assignees_btn)

        save_details_btn = QPushButton("Update details")
        save_details_btn.setObjectName("ghost_btn")
        save_details_btn.clicked.connect(self.save_details)
        sidebar_layout.addWidget(save_details_btn)

        sidebar_layout.addStretch()
        splitter.addWidget(sidebar)
        splitter.setSizes([660, 280])

        root.addWidget(splitter, stretch=1)

        footer = QHBoxLayout()
        footer.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setObjectName("ghost_btn")
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)
        root.addLayout(footer)

        self._set_composer_avatar()

    def _sidebar_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sidebar_label")
        return label

    def _set_composer_avatar(self):
        while self.composer_avatar_layout.count():
            child = self.composer_avatar_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        user = self.api_client.current_user or {}
        name = user.get("full_name") or user.get("username") or "You"
        avatar = AvatarLabel(name, user.get("id", 0), user.get("username", ""), size=36)
        self.composer_avatar_layout.addWidget(avatar)

    def _update_save_button(self):
        has_text = bool(self.comment_input.toPlainText().strip())
        has_files = bool(self.pending_attachment_paths)
        self.save_comment_btn.setEnabled(has_text or has_files)

    def _clear_comment_input(self):
        self.comment_input.clear()
        self.pending_attachment_paths.clear()
        self._refresh_pending_attachments_label()
        self._update_save_button()

    def attach_images(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Attach images",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp)",
        )
        for path in paths:
            if path and path not in self.pending_attachment_paths:
                self.pending_attachment_paths.append(path)
        self._refresh_pending_attachments_label()
        self._update_save_button()

    def _refresh_pending_attachments_label(self):
        count = len(self.pending_attachment_paths)
        if count == 0:
            self.pending_attachments_label.setText("")
        elif count == 1:
            self.pending_attachments_label.setText(f"1 image attached: {os.path.basename(self.pending_attachment_paths[0])}")
        else:
            self.pending_attachments_label.setText(f"{count} images attached")

    def _update_badges(self):
        status = self.task_data.get("status", "todo") if self.task_data else "todo"
        priority = self.task_data.get("priority", "medium") if self.task_data else "medium"

        status_styles = {
            "todo": ("TO DO", "#44546f", "#dfe1e6"),
            "in_progress": ("IN PROGRESS", "#0052cc", "#deebff"),
            "review": ("IN REVIEW", "#6554c0", "#eae6ff"),
            "done": ("DONE", "#00875a", "#e3fcef"),
        }
        status_text, status_color, status_bg = status_styles.get(status, status_styles["todo"])
        self.status_badge.setText(status_text)
        self.status_badge.setStyleSheet(
            f"padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: 700; "
            f"color: {status_color}; background-color: {status_bg};"
        )

        priority_styles = {
            "low": ("LOW", "#006644", "#e3fcef"),
            "medium": ("MEDIUM", "#974f0c", "#fff0b3"),
            "high": ("HIGH", "#bf2600", "#ffebe6"),
            "urgent": ("URGENT", "#ffffff", "#ff5630"),
        }
        priority_text, priority_color, priority_bg = priority_styles.get(priority, priority_styles["medium"])
        self.priority_badge.setText(priority_text)
        self.priority_badge.setStyleSheet(
            f"padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: 700; "
            f"color: {priority_color}; background-color: {priority_bg};"
        )

    def _set_assignee_emails_from_task(self, assignees):
        self.assignee_emails_list = []
        seen = set()
        for user in assignees or []:
            email = (user.get("email") or "").strip().lower()
            if email and email not in seen:
                seen.add(email)
                self.assignee_emails_list.append(email)
        self._refresh_assignee_rows()

    def _refresh_assignee_rows(self):
        while self.assignee_list_layout.count():
            item = self.assignee_list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        count = len(self.assignee_emails_list)
        self.assignee_count_label.setText(
            f"{count} assignee{'s' if count != 1 else ''}"
        )

        if not self.assignee_emails_list:
            empty = QLabel("No assignees yet")
            empty.setStyleSheet("color: #97a0af; font-size: 12px; padding: 8px;")
            self.assignee_list_layout.addWidget(empty)
            return

        for email in self.assignee_emails_list:
            row = QFrame()
            row.setStyleSheet(
                "QFrame { background: #ffffff; border: 1px solid #dfe1e6; border-radius: 4px; }"
            )
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(8, 4, 4, 4)

            email_label = QLabel(email)
            email_label.setStyleSheet("color: #172b4d; font-size: 12px;")
            email_label.setWordWrap(True)
            row_layout.addWidget(email_label, stretch=1)

            remove_btn = QPushButton("×")
            remove_btn.setFixedSize(24, 24)
            remove_btn.setToolTip("Remove assignee")
            remove_btn.setStyleSheet(
                "QPushButton { background: transparent; color: #626f86; border: none; font-size: 16px; font-weight: bold; }"
                "QPushButton:hover { color: #de350b; }"
            )
            remove_btn.clicked.connect(lambda _checked=False, e=email: self.remove_assignee_email(e))
            row_layout.addWidget(remove_btn)

            self.assignee_list_layout.addWidget(row)

    def add_assignee_email(self):
        email = self.add_assignee_input.text().strip().lower()
        if not email or "@" not in email:
            QMessageBox.warning(self, "Invalid email", "Enter a valid email address.")
            return
        if email in self.assignee_emails_list:
            QMessageBox.information(self, "Already added", f"{email} is already an assignee.")
            self.add_assignee_input.clear()
            return

        self.assignee_emails_list.append(email)
        self.add_assignee_input.clear()
        self._refresh_assignee_rows()

    def remove_assignee_email(self, email: str):
        if email in self.assignee_emails_list:
            self.assignee_emails_list.remove(email)
            self._refresh_assignee_rows()

    def _render_assignee_chips(self, assignees):
        self._set_assignee_emails_from_task(assignees)

    def load_task(self):
        self.task_data = self.api_client.get_task(self.task_id)
        if not self.task_data:
            QMessageBox.critical(self, "Error", "Could not load issue details.")
            self.reject()
            return

        title = self.task_data.get("title", "Untitled")
        self.setWindowTitle(f"PM-{self.task_id}: {title}")
        self.title_label.setText(title)
        self.description_view.setPlainText(self.task_data.get("description") or "")
        self._update_badges()

        status = self.task_data.get("status", "todo")
        for i in range(self.status_combo.count()):
            if self.status_combo.itemData(i) == status:
                self.status_combo.setCurrentIndex(i)
                break

        priority = self.task_data.get("priority", "medium")
        index = self.priority_combo.findText(priority)
        if index >= 0:
            self.priority_combo.setCurrentIndex(index)

        self._set_due_date_from_task(self.task_data.get("due_date"))

        self.users = self.api_client.get_users()
        self._set_assignee_emails_from_task(self.task_data.get("assignees", []))

    def load_comments(self):
        comments = self.api_client.get_task_comments(self.task_id)
        signature = tuple(
            (
                c.get("id"),
                c.get("body"),
                c.get("created_at"),
                tuple((a.get("id"), a.get("filename")) for a in c.get("attachments", [])),
            )
            for c in comments
        )
        if signature == self.last_comment_signature:
            return

        self.last_comment_signature = signature
        self.comment_count_label.setText(f"{len(comments)} comment{'s' if len(comments) != 1 else ''}")

        while self.activity_layout.count():
            child = self.activity_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not comments:
            empty = QLabel("There are no comments yet on this issue.")
            empty.setStyleSheet("color: #626f86; font-size: 13px; padding: 24px 12px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.activity_layout.addWidget(empty)
            return

        for comment in comments:
            self.activity_layout.addWidget(self._build_jira_comment(comment))

        self.activity_layout.addStretch()
        QTimer.singleShot(0, self._scroll_activity_to_bottom)

    def _scroll_activity_to_bottom(self):
        bar = self.activity_scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _build_jira_comment(self, comment):
        author = comment.get("author") or {}
        author_name = author.get("full_name") or author.get("username") or "Unknown"
        author_id = author.get("id") or comment.get("author_id") or 0

        row = QFrame()
        row.setObjectName("comment_row")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        layout.addWidget(
            AvatarLabel(author_name, author_id, author.get("username", ""), size=36),
            alignment=Qt.AlignmentFlag.AlignTop,
        )

        body_col = QVBoxLayout()
        body_col.setSpacing(8)

        meta = QHBoxLayout()
        meta.setSpacing(8)
        author_label = QLabel(author_name)
        author_label.setStyleSheet("color: #172b4d; font-size: 13px; font-weight: 700;")
        meta.addWidget(author_label)

        time_label = QLabel(_format_jira_time(comment.get("created_at", "")))
        time_label.setStyleSheet("color: #626f86; font-size: 12px;")
        meta.addWidget(time_label)

        if comment.get("source") == "email":
            source_label = QLabel("via email")
            source_label.setStyleSheet(
                "color: #0052cc; background: #deebff; padding: 2px 8px; "
                "border-radius: 3px; font-size: 10px; font-weight: 700;"
            )
            meta.addWidget(source_label)

        meta.addStretch()
        body_col.addLayout(meta)

        body_text = _strip_email_quotes(comment.get("body") or "")
        attachments = comment.get("attachments") or []

        if body_text:
            text = QLabel(body_text)
            text.setWordWrap(True)
            text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            text.setStyleSheet(
                "color: #172b4d; font-size: 13px; padding-top: 2px; "
                "line-height: 1.5;"
            )
            body_col.addWidget(text)
        elif attachments:
            image_only = QLabel("Shared an image")
            image_only.setStyleSheet("color: #626f86; font-size: 12px; font-style: italic;")
            body_col.addWidget(image_only)

        if attachments:
            images_row = QVBoxLayout()
            images_row.setSpacing(8)
            for attachment in attachments:
                image_label = self._build_attachment_preview(attachment)
                if image_label is not None:
                    images_row.addWidget(image_label)
            body_col.addLayout(images_row)

        layout.addLayout(body_col, stretch=1)
        return row

    def _build_attachment_preview(self, attachment):
        attachment_id = attachment.get("id")
        if not attachment_id:
            return None

        data = self.api_client.fetch_attachment_bytes(attachment_id)
        if not data:
            fallback = QLabel(f"Image: {attachment.get('filename', 'attachment')}")
            fallback.setStyleSheet("color: #626f86; font-size: 12px;")
            return fallback

        pixmap = QPixmap()
        if not pixmap.loadFromData(data):
            fallback = QLabel(f"Image: {attachment.get('filename', 'attachment')}")
            fallback.setStyleSheet("color: #626f86; font-size: 12px;")
            return fallback

        max_width = 320
        max_height = 240
        return ClickableImageLabel(pixmap, attachment.get("filename", "Image"), max_width, max_height)

    def save_assignees(self):
        result = self.api_client.update_task(
            self.task_id,
            assignee_emails=list(self.assignee_emails_list),
        )
        if result:
            self.task_data = result
            self._set_assignee_emails_from_task(result.get("assignees", []))
            QMessageBox.information(
                self,
                "Saved",
                f"{len(self.assignee_emails_list)} assignee(s) saved. New assignees were notified by email.",
            )
        else:
            QMessageBox.warning(self, "Error", "Failed to save assignees.")

    def _set_due_date_from_task(self, due_date_value):
        if not due_date_value:
            self.due_date_edit.setDate(NO_DUE_DATE)
            return
        try:
            normalized = str(due_date_value).replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            self.due_date_edit.setDate(QDate(dt.year, dt.month, dt.day))
        except (ValueError, TypeError):
            self.due_date_edit.setDate(NO_DUE_DATE)

    def _due_date_for_api(self):
        selected = self.due_date_edit.date()
        if selected <= NO_DUE_DATE:
            return None
        return selected.toString("yyyy-MM-dd") + "T12:00:00.000Z"

    def save_details(self):
        result = self.api_client.update_task(
            self.task_id,
            status=self.status_combo.currentData(),
            priority=self.priority_combo.currentText(),
            due_date=self._due_date_for_api(),
        )
        if result:
            self.task_data = result
            self._update_badges()
            QMessageBox.information(self, "Updated", "Issue details updated.")
        else:
            QMessageBox.warning(self, "Error", "Failed to update issue details.")

    def _export_chat_history(self, export_format: str):
        if not self.task_data:
            QMessageBox.warning(self, "Export", "Ticket details are not loaded yet.")
            return

        comments = self.api_client.get_task_comments(self.task_id)
        if export_format == "pdf":
            from src.services.chat_export import default_export_filename, export_chat_history_pdf

            default_name = default_export_filename(self.task_data, "pdf")
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Export chat history as PDF",
                default_name,
                "PDF files (*.pdf)",
            )
            if not path:
                return
            if not path.lower().endswith(".pdf"):
                path += ".pdf"

            try:
                export_chat_history_pdf(
                    path,
                    self.task_data,
                    comments,
                    self.api_client.fetch_attachment_bytes,
                )
            except ImportError:
                QMessageBox.warning(
                    self,
                    "Export",
                    "PDF export requires reportlab.\n\nRun: pip install reportlab python-docx",
                )
                return
            except Exception as exc:
                QMessageBox.critical(self, "Export failed", f"Could not create PDF:\n{exc}")
                return

            QMessageBox.information(self, "Export complete", f"Chat history saved to:\n{path}")
            return

        from src.services.chat_export import default_export_filename, export_chat_history_docx

        default_name = default_export_filename(self.task_data, "docx")
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export chat history as Word document",
            default_name,
            "Word documents (*.docx)",
        )
        if not path:
            return
        if not path.lower().endswith(".docx"):
            path += ".docx"

        try:
            export_chat_history_docx(
                path,
                self.task_data,
                comments,
                self.api_client.fetch_attachment_bytes,
            )
        except ImportError:
            QMessageBox.warning(
                self,
                "Export",
                "Word export requires python-docx.\n\nRun: pip install reportlab python-docx",
            )
            return
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", f"Could not create Word document:\n{exc}")
            return

        QMessageBox.information(self, "Export complete", f"Chat history saved to:\n{path}")

    def export_chat_pdf(self):
        self._export_chat_history("pdf")

    def export_chat_docx(self):
        self._export_chat_history("docx")

    def send_message(self):
        message = self.comment_input.toPlainText().strip()
        if not message and not self.pending_attachment_paths:
            return

        result = self.api_client.post_task_comment(
            self.task_id,
            message,
            file_paths=list(self.pending_attachment_paths) or None,
        )
        if result:
            self._clear_comment_input()
            self.last_comment_signature = None
            self.load_comments()
        else:
            error = self.api_client.last_error or "Unknown error"
            if "401" in error or "expired token" in error.lower():
                error = (
                    "Your session expired.\n\n"
                    "Log out and log in again, then retry your comment."
                )
            elif "422" in error or "valid dictionary" in error:
                error = (
                    "The backend server is out of date.\n\n"
                    "Close the backend window and restart start_backend.bat, "
                    "then try again."
                )
            QMessageBox.warning(self, "Error", f"Failed to save comment.\n\n{error}")

    def closeEvent(self, event):
        self.refresh_timer.stop()
        super().closeEvent(event)
