import sqlite3
import os

db_path = 'project_management.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    if 'users' in tables:
        cursor.execute("SELECT id, username, email FROM users")
        print("\nUsers:")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")
    
    if 'projects' in tables:
        cursor.execute("SELECT id, name, owner_id FROM projects")
        print("\nProjects:")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Name: {row[1]}, Owner ID: {row[2]}")
    
    conn.close()
else:
    print(f"Database file not found: {db_path}")
