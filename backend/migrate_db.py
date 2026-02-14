#!/usr/bin/env python3

import sqlite3
import os

def migrate_database():
    """Make project_id nullable in tasks table"""
    db_path = "project_management.db"
    
    if not os.path.exists(db_path):
        print("Database file does not exist. Creating new database...")
        from app.core.database import engine
        from app.models import Base
        Base.metadata.create_all(bind=engine)
        return
    
    print("Migrating database to make project_id nullable...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create backup of existing data
        cursor.execute("SELECT * FROM tasks")
        tasks_data = cursor.fetchall()
        
        # Get table structure
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        
        # Drop the tasks table
        cursor.execute("DROP TABLE tasks")
        
        # Create new tasks table with nullable project_id
        cursor.execute("""
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                status VARCHAR(20) DEFAULT 'TODO',
                priority VARCHAR(20) DEFAULT 'MEDIUM',
                project_id INTEGER,
                assignee_id INTEGER,
                due_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                FOREIGN KEY(project_id) REFERENCES projects(id),
                FOREIGN KEY(assignee_id) REFERENCES users(id)
            )
        """)
        
        # Restore data (if any)
        if tasks_data:
            placeholders = ",".join(["?" for _ in range(len(columns))])
            cursor.executemany(f"INSERT INTO tasks VALUES ({placeholders})", tasks_data)
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()