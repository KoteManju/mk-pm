#!/usr/bin/env python3
"""Test the task creation endpoint directly"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models import Task, User, Project

# Test database connection
db = SessionLocal()
try:
    # Check if project and user exist
    project = db.query(Project).filter(Project.id == 1).first()
    user = db.query(User).filter(User.id == 1).first()
    
    print(f"Project ID 1: {project.name if project else 'NOT FOUND'}")
    print(f"User ID 1: {user.username if user else 'NOT FOUND'}")
    
    # Try to create a task
    new_task = Task(
        title="dafsdf",
        description="strsdfsfing",
        status="todo",
        priority="medium",
        project_id=1,
        assignee_id=1,
        due_date="2026-02-14T02:23:35.303Z"
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    print(f"\n✅ Task created successfully!")
    print(f"   ID: {new_task.id}")
    print(f"   Title: {new_task.title}")
    print(f"   Status: {new_task.status}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
