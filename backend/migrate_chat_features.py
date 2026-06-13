#!/usr/bin/env python3
"""Add multi-assignee and task comment tables to an existing database."""

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
        CREATE TABLE IF NOT EXISTS task_assignees (
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (task_id, user_id),
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS task_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            body TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
        """
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO task_assignees (task_id, user_id)
        SELECT id, assignee_id FROM tasks WHERE assignee_id IS NOT NULL
        """
    )

    conn.commit()
    conn.close()
    print("Migration complete: task_assignees and task_comments tables are ready.")


if __name__ == "__main__":
    migrate()
