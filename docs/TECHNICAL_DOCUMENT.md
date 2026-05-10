# Karyaradhane – Technical Design Document

**Version:** 1.0.0  
**Date:** May 10, 2026  
**Repository:** https://github.com/KoteManju/mk-pm

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Backend – FastAPI Application](#5-backend--fastapi-application)
6. [Database Design](#6-database-design)
7. [API Reference](#7-api-reference)
8. [Authentication & Security](#8-authentication--security)
9. [Desktop Application – PySide6](#9-desktop-application--pyside6)
10. [UI Components](#10-ui-components)
11. [API Client Layer](#11-api-client-layer)
12. [Data Flow](#12-data-flow)
13. [Deployment Architecture](#13-deployment-architecture)
14. [Configuration Management](#14-configuration-management)
15. [Known Limitations & Future Work](#15-known-limitations--future-work)

---

## 1. Project Overview

**Karyaradhane** (meaning "Task Worship" in Sanskrit/Kannada) is a full-stack project management application inspired by Jira. It provides a desktop-native GUI for Windows users while the backend API and database are hosted on a FreeBSD server in Google Cloud Platform.

### Key Capabilities
- Kanban-style task board with drag-and-drop support
- Multi-project workspace with project filtering
- Issue creation with types: **Karya** (Task), **Katha** (Story), **Purana** (Epic), **Bug**
- Priority levels: Urgent, High, Medium, Low
- Task lifecycle: To Do → In Progress → Review → Done
- JWT-based user authentication
- Real-time auto-refresh (30-second polling)
- Dashboard with statistics

---

## 2. System Architecture

```
┌──────────────────────────────────────┐
│         WINDOWS DESKTOP              │
│                                      │
│  ┌────────────────────────────────┐  │
│  │   Karyaradhane.exe             │  │
│  │   (PySide6 / Qt for Python)    │  │
│  │                                │  │
│  │  MainWindow                    │  │
│  │   ├── DashboardWidget          │  │
│  │   ├── KanbanBoard              │  │
│  │   ├── ProjectListWidget        │  │
│  │   └── SettingsWidget           │  │
│  │                                │  │
│  │  APIClient (requests)          │  │
│  └────────────┬───────────────────┘  │
└───────────────┼──────────────────────┘
                │ HTTP/HTTPS (REST API)
                │ Bearer Token (JWT)
                ▼
┌──────────────────────────────────────┐
│      FREEBSD SERVER (GCP)            │
│                                      │
│  ┌────────┐     ┌──────────────────┐ │
│  │ Nginx  │────▶│ Uvicorn (8000)   │ │
│  │ :80    │     │                  │ │
│  │ :443   │     │  FastAPI App     │ │
│  └────────┘     │  ├── /api/auth   │ │
│                 │  ├── /api/users  │ │
│  Supervisor     │  ├── /api/projects│ │
│  (process mgr)  │  └── /api/tasks  │ │
│                 └────────┬─────────┘ │
│                          │           │
│                 ┌────────▼─────────┐ │
│                 │   SQLAlchemy ORM │ │
│                 └────────┬─────────┘ │
│                          │           │
│                 ┌────────▼─────────┐ │
│                 │  SQLite / PostgreSQL│
│                 └──────────────────┘ │
└──────────────────────────────────────┘
```

### Communication Protocol
- Desktop app communicates with the backend exclusively via **HTTP REST API**
- All requests carry a **Bearer JWT token** in the `Authorization` header
- CORS is configured to allow all origins (`*`) — should be restricted in production

---

## 3. Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Desktop UI | PySide6 (Qt for Python) | 6.10.2 |
| Desktop Language | Python | 3.11.9 |
| Backend Framework | FastAPI | 0.109.0 |
| ASGI Server | Uvicorn | 0.27.0 |
| ORM | SQLAlchemy | 2.0.25 |
| Database (dev) | SQLite | built-in |
| Database (prod) | PostgreSQL | 15.x |
| Authentication | python-jose (JWT) | 3.3.0 |
| Password Hashing | passlib (pbkdf2_sha256) | 1.7.4 |
| Data Validation | Pydantic v2 | 2.5.3 |
| HTTP Client | requests | latest |
| Web Server | Nginx | latest FreeBSD |
| Process Manager | Supervisor | latest FreeBSD |
| OS (server) | FreeBSD | 13.2 |
| Cloud Provider | Google Cloud Platform | — |

---

## 4. Project Structure

```
PM/
├── backend/                        # FastAPI backend application
│   ├── main.py                     # App entry point, router registration
│   ├── requirements.txt            # Python dependencies
│   ├── init_db.py                  # Database initializer (seeds default users)
│   ├── migrate_db.py               # Database migration helper
│   ├── .env.example                # Environment variable template
│   └── app/
│       ├── __init__.py
│       ├── core/
│       │   ├── config.py           # Settings via pydantic-settings
│       │   ├── database.py         # SQLAlchemy engine & session factory
│       │   └── security.py         # JWT creation/verification, password hashing
│       ├── models/
│       │   └── __init__.py         # SQLAlchemy ORM models (User, Project, Task)
│       ├── schemas/
│       │   └── __init__.py         # Pydantic schemas (request/response validation)
│       └── api/
│           └── routes/
│               ├── auth.py         # POST /api/auth/token (login)
│               ├── users.py        # CRUD /api/users
│               ├── projects.py     # CRUD /api/projects
│               └── tasks.py        # CRUD /api/tasks
│
├── desktop/                        # PySide6 desktop application
│   └── src/
│       ├── app.py                  # Application entry point
│       ├── api/
│       │   └── client.py           # HTTP API client wrapper (APIClient class)
│       └── ui/
│           ├── main_window.py      # MainWindow: sidebar nav + stacked views
│           ├── login_dialog.py     # Login dialog (modal)
│           ├── dashboard_widget.py # Dashboard with stats and quick actions
│           ├── kanban_board.py     # Kanban board (drag-drop, project filter)
│           ├── project_list.py     # Project grid with clickable cards
│           ├── task_dialog.py      # Full Jira-style issue creation dialog
│           ├── task_widget.py      # Simple task table view
│           ├── project_widget.py   # Simple project add view
│           └── settings_widget.py  # About / settings panel
│
├── deployment/                     # Server deployment files
│   ├── QUICKSTART.md               # Step-by-step deployment guide
│   ├── FREEBSD_GCP_SETUP.md        # Detailed FreeBSD/GCP instructions
│   ├── nginx.conf                  # Nginx reverse proxy config
│   ├── supervisor.ini              # Supervisor process config
│   ├── deploy.sh                   # Automated deployment shell script
│   ├── backup.sh                   # PostgreSQL backup script
│   ├── .env.example                # Production environment template
│   └── requirements-prod.txt       # Production Python dependencies
│
├── docs/
│   └── TECHNICAL_DOCUMENT.md       # This document
│
├── project_management.db           # Local SQLite database (development)
├── start_backend.bat               # Windows: start backend server
├── start_desktop.bat               # Windows: start desktop app
├── restart_backend.bat             # Windows: restart backend
└── health_check.py                 # API health/smoke tests
```

---

## 5. Backend – FastAPI Application

### Entry Point (`backend/main.py`)

The main FastAPI application is created with metadata, CORS middleware is applied, and routers are registered with prefixes:

```
GET  /           → Root info
GET  /health     → Health check → {"status": "healthy"}
POST /api/auth/token
GET  /api/users/
POST /api/users/
GET  /api/projects/
POST /api/projects/
GET  /api/tasks/
POST /api/tasks/
```

### Settings (`app/core/config.py`)

Uses `pydantic-settings` with `BaseSettings` for typed environment configuration:

| Setting | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./project_management.db` | SQLAlchemy DB URL |
| `SECRET_KEY` | `"your-secret-key-..."` | JWT signing key (must override in prod) |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token TTL |
| `ALLOWED_HOSTS` | `["*"]` | CORS allowed origins |

Values are loaded from `.env` file if present (case-sensitive).

### Database Session (`app/core/database.py`)

```python
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

A `get_db()` generator is used as a FastAPI dependency to inject and automatically close DB sessions:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 6. Database Design

### Enumerations

#### TaskStatus
| Value | Description |
|---|---|
| `todo` | Not started |
| `in_progress` | Actively being worked on |
| `review` | Pending review |
| `done` | Completed |

#### TaskPriority
| Value | Description |
|---|---|
| `low` | Low priority |
| `medium` | Default priority |
| `high` | High priority |
| `urgent` | Critical/blocking |

#### UserRole
| Value | Description |
|---|---|
| `admin` | Full system access |
| `manager` | Project management access |
| `member` | Standard user access |

> All enum values are stored as lowercase strings in the database using `values_callable=lambda x: [e.value for e in x]` in SQLAlchemy.

### Entity Relationship Diagram

```
┌──────────────┐          ┌──────────────────┐          ┌──────────────┐
│    users     │          │     projects     │          │    tasks     │
├──────────────┤          ├──────────────────┤          ├──────────────┤
│ id (PK)      │◄──────── │ id (PK)          │◄──────── │ id (PK)      │
│ username     │  owns    │ name             │  has     │ title        │
│ email        │          │ description      │          │ description  │
│ hashed_pass  │          │ owner_id (FK)    │          │ status       │
│ full_name    │          │ is_active        │          │ priority     │
│ role (enum)  │          │ created_at       │          │ project_id(FK│
│ is_active    │◄──────── │ updated_at       │          │ assignee_id  │
│ created_at   │ assigned │                  │          │ due_date     │
│ updated_at   │          └──────────────────┘          │ created_at   │
└──────────────┘                                        │ updated_at   │
                                                        └──────────────┘
```

### Table: `users`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, auto-increment |
| username | String(50) | UNIQUE, NOT NULL, indexed |
| email | String(100) | UNIQUE, NOT NULL, indexed |
| hashed_password | String(100) | NOT NULL |
| full_name | String(100) | nullable |
| role | Enum | default: `member` |
| is_active | Boolean | default: `True` |
| created_at | DateTime(tz) | server_default: now() |
| updated_at | DateTime(tz) | auto on update |

### Table: `projects`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, auto-increment |
| name | String(100) | NOT NULL |
| description | Text | nullable |
| owner_id | Integer | FK → users.id, NOT NULL |
| is_active | Boolean | default: `True` |
| created_at | DateTime(tz) | server_default: now() |
| updated_at | DateTime(tz) | auto on update |

### Table: `tasks`
| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, auto-increment |
| title | String(200) | NOT NULL |
| description | Text | nullable |
| status | Enum | default: `todo` |
| priority | Enum | default: `medium` |
| project_id | Integer | FK → projects.id, nullable |
| assignee_id | Integer | FK → users.id, nullable |
| due_date | DateTime | nullable |
| created_at | DateTime(tz) | server_default: now() |
| updated_at | DateTime(tz) | auto on update |

---

## 7. API Reference

### Authentication

#### `POST /api/auth/token`
Login and obtain a JWT access token.

**Request** (form-data, OAuth2 password grant):
```
username=admin&password=admin123
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error 401:** `{"detail": "Incorrect username or password"}`

---

### Projects

#### `GET /api/projects/`
Returns all projects.
```json
[
  {
    "id": 1,
    "name": "Website Redesign",
    "description": "Redesign company website",
    "owner_id": 1,
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

#### `POST /api/projects/`
Create a new project.  
**Status:** `201 Created`

**Request body:**
```json
{
  "name": "New Project",
  "description": "Optional description"
}
```

#### `GET /api/projects/{project_id}`
Retrieve a single project by ID.

#### `PUT /api/projects/{project_id}`
Update project fields (partial update supported via `exclude_unset=True`).

---

### Tasks

#### `GET /api/tasks/`
Returns tasks. Supports optional filtering:
- `?project_id=1` — filter by project
- `?skip=0&limit=100` — pagination

#### `POST /api/tasks/`
Create a new task.  
**Status:** `201 Created`

**Request body:**
```json
{
  "title": "Fix login bug",
  "description": "Users are unable to login on Firefox",
  "status": "todo",
  "priority": "high",
  "project_id": 1,
  "assignee_id": 2,
  "due_date": "2026-06-01T12:00:00.000Z"
}
```

#### `GET /api/tasks/{task_id}`
Retrieve a single task by ID.

#### `PUT /api/tasks/{task_id}`
Update task fields. Used by drag-and-drop on Kanban board to update `status`.

---

### Users

#### `GET /api/users/`
List all users.

#### `POST /api/users/`
Create a new user (passwords are hashed before storage).

#### `GET /api/users/{user_id}`
Retrieve a single user.

---

### Health

#### `GET /health`
```json
{"status": "healthy"}
```

---

## 8. Authentication & Security

### JWT Flow

```
Desktop App                     Backend API
    │                               │
    │── POST /api/auth/token ───────▶│
    │   (username + password)        │  Verify credentials
    │                               │  against DB (pbkdf2_sha256)
    │◄── {access_token, token_type} ─│
    │                               │
    │── GET /api/projects/ ─────────▶│
    │   Authorization: Bearer <token>│  Decode JWT
    │                               │  Verify signature + expiry
    │◄── [project list] ─────────────│
```

### Password Hashing

Uses `passlib` with `pbkdf2_sha256` scheme (not bcrypt, for FreeBSD compatibility):

```python
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
```

### JWT Token

- **Algorithm:** HS256
- **Payload:** `{"sub": username, "exp": <timestamp>}`
- **TTL:** 30 minutes (configurable)
- **Secret Key:** Must be set via `SECRET_KEY` env variable in production

### Security Headers (Nginx)

```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
```

### Rate Limiting (Nginx)

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req zone=api_limit burst=20 nodelay;
```

---

## 9. Desktop Application – PySide6

### Entry Point (`desktop/src/app.py`)

Creates `QApplication`, instantiates `APIClient`, creates `MainWindow`, and starts the Qt event loop.

### Main Window (`main_window.py`)

`MainWindow(QMainWindow)` provides:
- **Sidebar navigation** using `QListWidget` with item-based tab switching
- **Stacked widget** (`QStackedWidget`) for page content
- **Login flow** — shows `LoginDialog` on startup; main UI only becomes visible after successful authentication
- **Navigation items:** Dashboard, Projects, Kanban Board, Settings
- **Global logout** button (red, bottom of sidebar)

```
MainWindow
 ├── Sidebar (QFrame, blue #1976D2)
 │   ├── Title: "Karyaradhane"
 │   ├── QListWidget (nav items)
 │   └── Logout Button
 └── QStackedWidget
     ├── DashboardWidget    (index 0)
     ├── ProjectListWidget  (index 1)
     ├── KanbanBoard        (index 2)
     └── SettingsWidget     (index 3)
```

### Color Theme

| Element | Color |
|---|---|
| Sidebar background | `#1976D2` (Material Blue) |
| Sidebar selected item | `#1565C0` |
| Primary button | `#1976D2` |
| Button hover | `#1565C0` |
| Button pressed | `#0D47A1` |
| Page background | `#f5f5f5` |
| Card background | `white` |
| Primary text | `#172b4d` |
| Secondary text | `#5e6c84` |

---

## 10. UI Components

### DashboardWidget (`dashboard_widget.py`)

Displays:
- **Title:** "📊 Karyaradhane Dashboard"
- **Statistics cards:** Total Projects, Active Tasks, Completed Tasks (auto-populated from API)
- **Quick Actions:** New Issue, New Project, View Board buttons
- **Recent Activity** section
- **Auto-refresh** every 30 seconds via `QTimer`

### KanbanBoard (`kanban_board.py`)

The most complex UI component. Consists of:

#### `TaskCard(QFrame)`
- Displays: title, description (truncated to 100 chars), priority badge, task ID
- **Drag source:** Implements `mousePressEvent` + `mouseMoveEvent` to initiate `QDrag`
- MIME data format: `"application/x-taskdata"` containing the task ID as bytes

#### `KanbanColumn(QFrame)`
- **Drop target:** Accepts drops of type `"application/x-taskdata"`
- On drop: calls `api_client.update_task_status(task_id, self.status)` and refreshes board
- Visual drag feedback: dashed border appears on `dragEnterEvent`
- Contains a `QScrollArea` for overflow tasks

#### `KanbanBoard(QWidget)`
- Four columns: To Do, In Progress, Review, Done
- **Project filter dropdown** (`QComboBox`) — loads projects from API, filters tasks by `project_id`
- **Refresh button** — manual refresh
- **Quick Task button** — `QInputDialog` for fast task creation
- **Auto-refresh** every 30 seconds

```
KanbanBoard
 ├── Header (title, project filter, refresh, quick task)
 └── Columns (HBoxLayout)
     ├── KanbanColumn ("📝 To Do",    status="todo")
     ├── KanbanColumn ("🔄 In Progress", status="in_progress")
     ├── KanbanColumn ("👀 Review",    status="review")
     └── KanbanColumn ("✅ Done",      status="done")
```

### ProjectListWidget (`project_list.py`)

- **Grid layout** (4 columns) of `ProjectCard` widgets
- Click on a card → navigates to Kanban board filtered by that project
- **Create Project** button triggers `ProjectCreationDialog`

#### `ProjectCreationDialog(QDialog)`
- Input: project name (required), description (optional)
- On submit: calls `api_client.create_project()`, shows success message, closes dialog

### TaskCreationDialog (`task_dialog.py`)

Full Jira-style issue creation form:

| Field | Widget | Notes |
|---|---|---|
| Issue Type | QComboBox | Karya, Bug, Katha, Purana |
| Summary | QLineEdit | Required |
| Description | QTextEdit | Optional |
| Project | QComboBox | Loaded from API |
| Priority | QComboBox | Highest → Lowest, mapped to API values |
| Status | QComboBox | To Do → Done, mapped to API values |
| Assignee | QComboBox | Loaded from API |
| Due Date | QDateEdit | Optional |

**Priority mapping:**
```python
priority_map = {
    "🔴 Highest": "urgent",
    "🟠 High": "high",
    "🟡 Medium": "medium",
    "🟢 Low": "low",
    "⚪ Lowest": "low"
}
```

**Status mapping:**
```python
status_map = {
    "📝 To Do": "todo",
    "🔄 In Progress": "in_progress",
    "👀 In Review": "review",
    "✅ Done": "done"
}
```

### LoginDialog (`login_dialog.py`)

Simple modal dialog:
- Username and password fields (`QLineEdit`)
- Enter key triggers login on both fields
- On success: `self.accept()` — main window becomes visible
- On failure: clears password field, shows error `QMessageBox`

---

## 11. API Client Layer

### `APIClient` (`desktop/src/api/client.py`)

Singleton-style class wrapping all HTTP communication using the `requests` library.

```python
class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
```

#### Key Methods

| Method | HTTP | Endpoint | Returns |
|---|---|---|---|
| `login(username, password)` | POST | `/api/auth/token` | `bool` |
| `register(username, email, password)` | POST | `/api/auth/register` | `bool` |
| `get_current_user()` | GET | `/api/users/me` | `Dict` |
| `get_projects()` | GET | `/api/projects/` | `List[Dict]` |
| `create_project(name, description)` | POST | `/api/projects/` | `Dict` |
| `get_tasks(project_id=None)` | GET | `/api/tasks/` | `List[Dict]` |
| `create_task(title, ...)` | POST | `/api/tasks/` | `Dict` |
| `update_task_status(task_id, status)` | PUT | `/api/tasks/{id}` | `Dict` |

#### Authentication Header

```python
def get_headers(self):
    headers = {"Content-Type": "application/json"}
    if self.token:
        headers["Authorization"] = f"Bearer {self.token}"
    return headers
```

---

## 12. Data Flow

### Login Flow
```
1. User enters credentials in LoginDialog
2. APIClient.login() → POST /api/auth/token (form-data)
3. Backend verifies password hash against DB
4. Backend returns JWT token
5. APIClient stores token in self.token
6. LoginDialog.accept() is called → main window becomes visible
```

### Task Creation Flow
```
1. User opens TaskCreationDialog (from toolbar or Quick Task)
2. User fills out form fields
3. On submit: TaskCreationDialog.create_task() called
4. APIClient.create_task() → POST /api/tasks/
5. Backend validates via Pydantic TaskCreate schema
6. SQLAlchemy creates record in tasks table
7. Backend returns Task object (201 Created)
8. Dialog shows QMessageBox success
9. Dialog closes (self.accept())
10. Parent widget calls refresh_data()
```

### Kanban Drag-and-Drop Flow
```
1. User clicks and drags TaskCard
2. mouseMoveEvent creates QDrag with MIME type "application/x-taskdata"
3. MIME data contains task_id as bytes
4. User drops card onto KanbanColumn
5. KanbanColumn.dropEvent() extracts task_id from MIME data
6. APIClient.update_task_status(task_id, column.status) → PUT /api/tasks/{id}
7. Backend updates task.status in database
8. KanbanBoard.refresh_data() reloads all tasks
```

### Project-to-Kanban Navigation Flow
```
1. User clicks a ProjectCard in ProjectListWidget
2. ProjectCard.view_project() calls parent_widget.view_project_tasks(project_id, name)
3. ProjectListWidget calls MainWindow.show_project_kanban(project_id, name)
4. MainWindow switches stacked widget to KanbanBoard (index 2)
5. KanbanBoard.filter_by_project(project_id) is called
6. Project filter combo updates to show selected project
7. KanbanBoard.refresh_data() loads tasks filtered by project_id
```

---

## 13. Deployment Architecture

### Production Setup (FreeBSD on GCP)

```
Internet
    │
    ▼
Nginx (:80 / :443)
    │
    ├── /api/*  ──────▶  Uvicorn (127.0.0.1:8000)
    │                         │
    │                    FastAPI Application
    │                         │
    │                    SQLAlchemy ORM
    │                         │
    │                    PostgreSQL 15
    │
    └── /health ─────▶  Uvicorn (127.0.0.1:8000)
```

### Process Management (Supervisor)

```ini
[program:karyaradhane]
command=/opt/karyaradhane/backend/venv/bin/uvicorn main:app
        --host 127.0.0.1 --port 8000 --workers 2
directory=/opt/karyaradhane/backend
environment=PYTHONPATH="/opt/karyaradhane/backend"
autostart=true
autorestart=true
```

### Nginx Reverse Proxy

```nginx
upstream karyaradhane_backend {
    server 127.0.0.1:8000;
}

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://karyaradhane_backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### Desktop Distribution

The PySide6 desktop application is packaged with **PyInstaller** into a Windows `.exe`:
- End users download the installer
- The exe connects to the hosted backend API URL
- No server installation needed on client machines

---

## 14. Configuration Management

### Backend `.env` File

```env
DATABASE_URL=postgresql://karyaradhane_user:password@localhost/karyaradhane
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Desktop API URL Configuration

In `desktop/src/api/client.py`:
```python
# Development
APIClient(base_url="http://localhost:8000")

# Production
APIClient(base_url="http://YOUR_SERVER_IP")
```

For production builds, this should be set via an environment variable or a config file bundled with the installer.

### Default Credentials (Development)

| Username | Password | Role |
|---|---|---|
| admin | admin123 | admin |
| user | user123 | member |

> **Security Warning:** Change all default credentials before production deployment.

---

## 15. Known Limitations & Future Work

### Current Limitations

| Area | Limitation |
|---|---|
| Authentication | Projects route uses hardcoded `owner_id=1` — needs JWT middleware on API routes |
| Authorization | No route-level auth guards — any authenticated user can modify any resource |
| Offline mode | Desktop app fails silently when backend is unreachable |
| Error handling | Some API errors are only printed to console, not shown to user |
| CORS | `allow_origins=["*"]` — must be restricted in production |
| Refresh | Uses polling (30s timer) instead of WebSockets for real-time updates |
| Search | No search/filter functionality for tasks |
| Pagination | Backend supports `skip`/`limit` but desktop always fetches first 100 items |
| SSL | Nginx config has HTTPS commented out — must be enabled for production |

### Recommended Improvements

1. **Add JWT middleware** to all API routes (Depends on current_user)
2. **Restrict CORS** to the specific server/domain in production
3. **Add Alembic** for proper database migration management
4. **Implement WebSocket** for real-time kanban updates
5. **Add task search and filter** by assignee, priority, date range
6. **Implement file attachments** on tasks
7. **Add user assignment UI** — currently `assignee_id` in dialog but not wired to user list
8. **Sentry integration** for error tracking (requirements-prod.txt already includes it)
9. **Automated testing** — add pytest test suite for API routes
10. **Desktop auto-updater** — check for new version on startup

---

*Document generated: May 10, 2026 | Karyaradhane v1.0.0*
