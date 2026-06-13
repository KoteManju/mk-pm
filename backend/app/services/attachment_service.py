import mimetypes
import uuid
from pathlib import Path
from typing import List

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import CommentAttachment

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
}
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024


def get_upload_dir() -> Path:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _safe_extension(filename: str, content_type: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}:
        return suffix
    guessed = mimetypes.guess_extension(content_type or "")
    return guessed or ".png"


def save_attachment_bytes(
    db: Session,
    comment_id: int,
    data: bytes,
    filename: str,
    content_type: str,
) -> CommentAttachment:
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(f"Unsupported image type: {content_type}")

    if len(data) > MAX_ATTACHMENT_BYTES:
        raise ValueError("Image is too large (max 10 MB)")

    stored_name = f"{uuid.uuid4().hex}{_safe_extension(filename, content_type)}"
    file_path = get_upload_dir() / stored_name
    file_path.write_bytes(data)

    attachment = CommentAttachment(
        comment_id=comment_id,
        filename=Path(filename).name or stored_name,
        stored_name=stored_name,
        content_type=content_type,
        file_size=len(data),
    )
    db.add(attachment)
    return attachment


async def save_upload_files(
    db: Session,
    comment_id: int,
    uploads: List[UploadFile],
) -> List[CommentAttachment]:
    saved: List[CommentAttachment] = []
    for upload in uploads:
        if not upload.filename:
            continue
        data = await upload.read()
        if not data:
            continue
        content_type = upload.content_type or mimetypes.guess_type(upload.filename)[0] or "image/png"
        saved.append(
            save_attachment_bytes(db, comment_id, data, upload.filename, content_type)
        )
    return saved


def get_attachment_file_path(attachment: CommentAttachment) -> Path:
    return get_upload_dir() / attachment.stored_name
