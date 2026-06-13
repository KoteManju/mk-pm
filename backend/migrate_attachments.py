#!/usr/bin/env python3
"""Add comment attachment table for image uploads."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "project_management.db"


def migrate():
    if not DB_PATH.exists():
        print("No database found. Run init_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS comment_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            stored_name TEXT NOT NULL UNIQUE,
            content_type TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comment_id) REFERENCES task_comments (id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()
    conn.close()
    print("Migration complete: comment_attachments table is ready.")


if __name__ == "__main__":
    migrate()
