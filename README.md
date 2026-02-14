# Project Management System

A full-stack project management application with a Python PySide6 desktop client and FastAPI backend.

## Architecture

- **Desktop Application**: Python + PySide6 (packaged as .exe with PyInstaller)
- **Backend API**: FastAPI + SQLAlchemy + PostgreSQL
- **Authentication**: JWT tokens
- **Infrastructure**: FreeBSD + Nginx + Supervisor

## Features

- **Project Management**: Create and manage projects
- **Task Management**: Create, assign, and track tasks
- **User Authentication**: Secure login with JWT tokens
- **Cross-platform Desktop App**: Native Qt-based interface
- **REST API**: Full-featured API for all operations

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── core/           # Core configuration
│   ├── main.py             # FastAPI app entry point
│   └── pyproject.toml      # Backend dependencies
├── desktop/                # PySide6 desktop app
│   ├── src/
│   │   ├── ui/             # UI components
│   │   └── api/            # API client
│   ├── main.py             # Desktop app entry point
│   ├── pyproject.toml      # Desktop dependencies
│   └── build.spec          # PyInstaller configuration
└── deployment/             # Infrastructure configs
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- pip or poetry for dependency management

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   # or with dev dependencies
   pip install -e ".[dev]"
   ```

3. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Setup database:**
   ```bash
   # Create PostgreSQL database
   createdb project_management
   
   # Run migrations (you'll need to create them)
   alembic init alembic
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

5. **Run the backend:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   API will be available at: http://localhost:8000
   API docs: http://localhost:8000/docs

### Desktop App Setup

1. **Navigate to desktop directory:**
   ```bash
   cd desktop
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   # or with dev dependencies
   pip install -e ".[dev]"
   ```

3. **Run the desktop app:**
   ```bash
   python main.py
   ```

### Building Executable

1. **Install packaging dependencies:**
   ```bash
   pip install -e ".[packaging]"
   ```

2. **Build with PyInstaller:**
   ```bash
   pyinstaller build.spec
   ```

   The executable will be in the `dist/` directory.

## Development

### Backend Development

- **API Documentation**: Available at `/docs` when running
- **Database Models**: Defined in `app/models/`
- **API Routes**: Organized in `app/api/routes/`
- **Authentication**: JWT-based, configured in `app/core/security.py`

### Desktop Development

- **UI Components**: Located in `src/ui/`
- **API Client**: HTTP client in `src/api/client.py`
- **Main Window**: Entry point in `src/ui/main_window.py`

### Code Quality

Both projects include:
- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pytest**: Testing framework

Run quality checks:
```bash
black .
isort .
mypy .
pytest
```

## Database Schema

### Users
- id, username, email, hashed_password
- full_name, role, is_active
- created_at, updated_at

### Projects  
- id, name, description, owner_id
- is_active, created_at, updated_at

### Tasks
- id, title, description, status, priority
- project_id, assignee_id, due_date
- created_at, updated_at

## API Endpoints

### Authentication
- `POST /api/auth/token` - Login and get JWT token

### Users
- `GET /api/users/` - List users
- `POST /api/users/` - Create user
- `GET /api/users/{id}` - Get user details

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project

### Tasks
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task

## Deployment (FreeBSD)

### PostgreSQL Setup
```bash
# Install PostgreSQL
pkg install postgresql15-server

# Initialize database
service postgresql initdb

# Start PostgreSQL
service postgresql start
```

### Python Environment
```bash
# Install Python
pkg install python311

# Create virtual environment
python3.11 -m venv /opt/project-management
source /opt/project-management/bin/activate
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Supervisor Configuration
```ini
[program:project-management-api]
command=/opt/project-management/bin/uvicorn main:app --host 127.0.0.1 --port 8000
directory=/opt/project-management/app
user=www
autostart=true
autorestart=true
```

## Configuration

### Environment Variables

Create `.env` file in backend directory:

```bash
DATABASE_URL=postgresql://user:pass@localhost/project_management
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_HOSTS=["http://localhost:3000"]
```

### Desktop Configuration

The desktop app connects to the API at `http://localhost:8000` by default. This can be configured in the `APIClient` class.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run code quality checks
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the code structure in this README