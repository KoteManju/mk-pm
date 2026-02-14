#!/usr/bin/env python3
"""
Database initialization script
Creates tables and adds sample data for testing
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base, User, Project, Task
from app.core.security import get_password_hash
import datetime

def init_database():
    """Initialize database with tables and sample data"""
    print("🗄️ Initializing database...")
    
    # Create engine and tables
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if we already have data
        existing_user = db.query(User).first()
        if existing_user:
            print("✅ Database already has data")
            return
        
        print("📝 Creating sample data...")
        
        # Create sample users
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role="admin"  # Use lowercase enum value
        )
        db.add(admin_user)
        
        regular_user = User(
            username="user",
            email="user@example.com", 
            hashed_password=get_password_hash("user123"),
            full_name="Regular User",
            role="member"  # Use lowercase enum value
        )
        db.add(regular_user)
        
        # Commit users first to get IDs
        db.commit()
        db.refresh(admin_user)
        db.refresh(regular_user)
        
        # Create sample project
        sample_project = Project(
            name="Sample Project",
            description="A sample project to test the system",
            owner_id=admin_user.id
        )
        db.add(sample_project)
        db.commit()
        db.refresh(sample_project)
        
        # Create sample tasks
        tasks = [
            Task(
                title="Setup Development Environment",
                description="Install required tools and dependencies",
                project_id=sample_project.id,
                assignee_id=admin_user.id,
                status="done",  # Use lowercase enum value
                priority="high"  # Use lowercase enum value
            ),
            Task(
                title="Design Database Schema",
                description="Create the database models and relationships",
                project_id=sample_project.id,
                assignee_id=admin_user.id,
                status="done",  # Use lowercase enum value
                priority="medium"  # Use lowercase enum value
            ),
            Task(
                title="Implement API Endpoints",
                description="Create REST API endpoints for all operations",
                project_id=sample_project.id,
                assignee_id=regular_user.id,
                status="in_progress",  # Use lowercase enum value
                priority="high"  # Use lowercase enum value
            ),
            Task(
                title="Create Desktop Application",
                description="Build the PySide6 desktop client",
                project_id=sample_project.id,
                assignee_id=regular_user.id,
                status="todo",  # Use lowercase enum value
                priority="medium"  # Use lowercase enum value
            ),
        ]
        
        for task in tasks:
            db.add(task)
        
        db.commit()
        
        print("✅ Database initialized successfully!")
        print("")
        print("📋 Sample data created:")
        print("   Users: admin/admin123, user/user123")
        print("   Project: Sample Project")
        print("   Tasks: 4 sample tasks")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()