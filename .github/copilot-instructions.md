# Project Management Software

This workspace contains a full-stack project management application:

## Architecture
- **Desktop App**: Python + PySide6 (packaged with PyInstaller)
- **Backend API**: FastAPI + SQLAlchemy + PostgreSQL
- **Authentication**: JWT tokens
- **Infrastructure**: FreeBSD + Nginx + Supervisor

## Development Stack
- Python 3.11+
- PySide6 for desktop GUI
- FastAPI for REST API
- SQLAlchemy for ORM
- PostgreSQL for database
- Redis for caching (optional)
- JWT for authentication

## Project Structure
- `desktop/` - PySide6 desktop application
- `backend/` - FastAPI backend API
- `docs/` - Documentation
- `deployment/` - Infrastructure configs

## Development Guidelines
- Use type hints throughout Python code
- Follow FastAPI best practices for API design
- Use SQLAlchemy declarative models
- Implement proper error handling
- Use async/await patterns where appropriate
- Follow PEP 8 style guidelines