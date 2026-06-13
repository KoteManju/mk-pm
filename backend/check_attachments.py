"""Quick check: comments with image attachments in DB and on disk."""
import requests
from pathlib import Path

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import TaskComment, CommentAttachment
from sqlalchemy.orm import joinedload

BASE = "http://127.0.0.1:8000"


def main():
    upload_dir = Path(settings.UPLOAD_DIR)
    print(f"Upload dir: {upload_dir.resolve()}")
    print(f"Files on disk: {len(list(upload_dir.glob('*'))) if upload_dir.exists() else 0}")

    db = SessionLocal()
    attachments = db.query(CommentAttachment).all()
    print(f"DB attachments: {len(attachments)}")
    for att in attachments:
        path = upload_dir / att.stored_name
        print(
            f"  id={att.id} comment_id={att.comment_id} "
            f"filename={att.filename} exists={path.exists()} size={att.file_size}"
        )

    comments = (
        db.query(TaskComment)
        .options(joinedload(TaskComment.attachments))
        .order_by(TaskComment.id)
        .all()
    )
    print(f"Comments: {len(comments)}")
    for c in comments:
        atts = c.attachments or []
        print(f"  comment {c.id}: {repr((c.body or '')[:50])} attachments={len(atts)}")
    db.close()

    try:
        health = requests.get(f"{BASE}/health", timeout=5).json()
        print("Health:", health)
    except Exception as exc:
        print("Backend unreachable:", exc)
        return

    token = requests.post(
        f"{BASE}/api/auth/token",
        data={"username": "admin", "password": "admin123"},
        timeout=10,
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    api_comments = requests.get(f"{BASE}/api/tasks/1/comments", headers=headers, timeout=10).json()
    print(f"API task 1 comments: {len(api_comments)}")
    for c in api_comments:
        for a in c.get("attachments") or []:
            url = f"{BASE}/api/tasks/attachments/{a['id']}"
            resp = requests.get(url, headers=headers, timeout=10)
            print(
                f"  attachment {a['id']} ({a['filename']}): "
                f"HTTP {resp.status_code}, {len(resp.content)} bytes"
            )


if __name__ == "__main__":
    main()
