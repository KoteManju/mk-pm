#!/usr/bin/env python3
"""Add email comment tracking columns and processed email table."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "project_management.db"


def migrate():
    if not DB_PATH.exists():
        print("No database found. Run init_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns = {row[1] for row in cursor.execute("PRAGMA table_info(task_comments)").fetchall()}
    if "source" not in columns:
        cursor.execute("ALTER TABLE task_comments ADD COLUMN source TEXT DEFAULT 'app'")
    if "external_message_id" not in columns:
        cursor.execute("ALTER TABLE task_comments ADD COLUMN external_message_id TEXT")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_emails (
            message_id TEXT PRIMARY KEY,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ix_task_comments_external_message_id
        ON task_comments (external_message_id)
        WHERE external_message_id IS NOT NULL
        """
    )

    conn.commit()
    conn.close()
    print("Migration complete: email comment columns are ready.")


if __name__ == "__main__":
    migrate()
