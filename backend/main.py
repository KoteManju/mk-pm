from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import SessionLocal
from app.core.config import settings
from app.services.email_service import start_email_poller, stop_email_poller


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_email_poller(SessionLocal)
    yield
    stop_email_poller()


app = FastAPI(
    title="Project Management API",
    description="A comprehensive project management API built with FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Project Management API", "version": "1.0.0"}


try:
    from app.api.routes import auth, projects, tasks, users
    app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
except ImportError as e:
    print(f"Warning: Could not import routes: {e}")
    print("API running with basic functionality only")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "email_enabled": settings.EMAIL_ENABLED,
        "attachments_enabled": True,
        "version": "1.1.0",
    }
