import hashlib
import os
import re
import secrets
import smtplib
import imaplib
import threading
import time
from email.message import EmailMessage
from email.utils import parseaddr, formataddr
from email.header import decode_header
from email import message_from_bytes
from typing import List, Optional, Set

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User, Task, TaskComment, ProcessedEmail
from app.services.attachment_service import save_attachment_bytes, get_attachment_file_path

TASK_SUBJECT_RE = re.compile(r"\[PM-(\d+)\]", re.IGNORECASE)
REPLY_MARKERS = (
    "-----original message-----",
    "----- forwarded message -----",
    "________________________________",
    "from:",
    "sent from my iphone",
    "sent from my android",
)


def task_subject(task_id: int, title: str) -> str:
    return f"[PM-{task_id}] {title}"


def get_or_create_user_by_email(db: Session, email: str) -> User:
    normalized = email.strip().lower()
    if not normalized or "@" not in normalized:
        raise ValueError(f"Invalid email address: {email}")

    user = db.query(User).filter(User.email == normalized).first()
    if user:
        return user

    local_part = normalized.split("@")[0]
    username = re.sub(r"[^a-zA-Z0-9_]", "_", local_part) or "user"
    base_username = username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    display_name = local_part.replace(".", " ").replace("_", " ").title()
    user = User(
        username=username,
        email=normalized,
        hashed_password=get_password_hash(secrets.token_urlsafe(32)),
        full_name=display_name,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def resolve_assignees(
    db: Session,
    assignee_ids: Optional[List[int]] = None,
    assignee_emails: Optional[List[str]] = None,
) -> List[User]:
    users: dict[int, User] = {}

    if assignee_ids:
        for user in db.query(User).filter(User.id.in_(assignee_ids)).all():
            users[user.id] = user
        if len(users) != len(set(assignee_ids)):
            missing = set(assignee_ids) - set(users.keys())
            raise ValueError(f"Invalid assignee IDs: {sorted(missing)}")

    if assignee_emails:
        for email in assignee_emails:
            email = email.strip()
            if not email:
                continue
            user = get_or_create_user_by_email(db, email)
            users[user.id] = user

    return list(users.values())


def _strip_reply_text(text: str) -> str:
    if not text:
        return ""

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cleaned: List[str] = []

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        if stripped.startswith(">"):
            break
        if any(marker in lower for marker in REPLY_MARKERS):
            break
        if lower.startswith("on ") and " wrote:" in lower:
            break

        cleaned.append(line.rstrip())

    body = "\n".join(cleaned).strip()
    return body


def _extract_plain_text(raw_email: bytes) -> str:
    message = message_from_bytes(raw_email)
    parts: List[str] = []

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    parts.append(payload.decode(charset, errors="replace"))
    else:
        if message.get_content_type() == "text/plain":
            payload = message.get_payload(decode=True)
            if payload:
                charset = message.get_content_charset() or "utf-8"
                parts.append(payload.decode(charset, errors="replace"))

    return _strip_reply_text("\n".join(parts).strip())


def _decode_mime_filename(raw_filename: Optional[str]) -> str:
    if not raw_filename:
        return "image.png"
    decoded_parts = []
    for part, encoding in decode_header(raw_filename):
        if isinstance(part, bytes):
            decoded_parts.append(part.decode(encoding or "utf-8", errors="replace"))
        else:
            decoded_parts.append(part)
    return "".join(decoded_parts) or "image.png"


def _extract_image_attachments(message) -> List[dict]:
    images = []
    seen_hashes = set()

    for part in message.walk():
        content_type = part.get_content_type()
        if not content_type.startswith("image/"):
            continue

        payload = part.get_payload(decode=True)
        if not payload:
            continue

        digest = hashlib.md5(payload).hexdigest()
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)

        filename = _decode_mime_filename(part.get_filename())
        images.append(
            {
                "data": payload,
                "filename": filename,
                "content_type": content_type,
            }
        )

    return images


def extract_task_id_from_subject(subject: str) -> Optional[int]:
    match = TASK_SUBJECT_RE.search(subject or "")
    if not match:
        return None
    return int(match.group(1))


def extract_sender_email(from_header: str) -> Optional[str]:
    _, address = parseaddr(from_header or "")
    return address.strip().lower() if address else None


def is_email_configured() -> bool:
    return bool(settings.EMAIL_ENABLED and settings.SMTP_HOST and settings.SMTP_FROM)


def is_imap_configured() -> bool:
    return bool(settings.IMAP_HOST and settings.IMAP_USER and settings.IMAP_PASSWORD)


def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachments: Optional[List[dict]] = None,
) -> bool:
    if not is_email_configured():
        print(f"Email disabled. Would send to {to_email}: {subject}")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((settings.EMAIL_FROM_NAME, settings.SMTP_FROM))
    message["To"] = to_email
    message["Reply-To"] = settings.SMTP_FROM
    message.set_content(body)

    for attachment in attachments or []:
        maintype, _, subtype = attachment["content_type"].partition("/")
        if not subtype:
            maintype, subtype = "application", "octet-stream"
        message.add_attachment(
            attachment["data"],
            maintype=maintype,
            subtype=subtype,
            filename=attachment["filename"],
        )

    try:
        if settings.SMTP_USE_SSL:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
            if settings.SMTP_USE_TLS:
                server.starttls()

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.send_message(message)
        server.quit()
        print(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as exc:
        print(f"Failed to send email to {to_email}: {exc}")
        return False


def notify_assignment(db: Session, task: Task, assignee: User, assigned_by: Optional[str] = None) -> None:
    if not assignee.email or "@" not in assignee.email:
        print(f"Skipping assignment email for user {assignee.id}: no valid email")
        return
    if assignee.email.endswith("@example.com"):
        print(f"Skipping assignment email for {assignee.email}: sample/placeholder address")
        return

    subject = f"[PM-{task.id}] You were assigned: {task.title}"
    assigner = assigned_by or "Project Management"
    body = (
        f"Hello {assignee.full_name or assignee.username},\n\n"
        f"You have been assigned to ticket PM-{task.id}: {task.title}\n\n"
        f"Description:\n{task.description or '(No description)'}\n\n"
        f"Assigned by: {assigner}\n\n"
        f"Reply to this email to post a comment on the ticket.\n"
        f"Keep [PM-{task.id}] in the subject line.\n"
    )
    send_email(assignee.email, subject, body)


def _comment_email_attachments(comment: TaskComment) -> List[dict]:
    attachments = []
    for attachment in getattr(comment, "attachments", []) or []:
        file_path = get_attachment_file_path(attachment)
        if not file_path.exists():
            continue
        attachments.append(
            {
                "filename": attachment.filename,
                "content_type": attachment.content_type,
                "data": file_path.read_bytes(),
            }
        )
    return attachments


def notify_new_comment(
    db: Session,
    task: Task,
    comment: TaskComment,
    author: User,
    recipients: List[User],
) -> None:
    subject = f"[PM-{task.id}] New comment on: {task.title}"
    email_attachments = _comment_email_attachments(comment)

    for recipient in recipients:
        if recipient.id == author.id:
            continue
        body = (
            f"Hello {recipient.full_name or recipient.username},\n\n"
            f"{author.full_name or author.username} commented on PM-{task.id}:\n\n"
            f"{comment.body or '(No text)'}\n"
        )
        if email_attachments:
            body += (
                f"\n{len(email_attachments)} image attachment(s) are included with this email.\n"
                f"You can also reply to this email to respond on the ticket.\n"
            )
        else:
            body += "\nReply to this email to respond on the ticket.\n"
        body += f"Keep [PM-{task.id}] in the subject line.\n"
        send_email(recipient.email, subject, body, attachments=email_attachments)


def process_inbound_email(db: Session, raw_email: bytes, message_id: str) -> bool:
    if db.query(ProcessedEmail).filter(ProcessedEmail.message_id == message_id).first():
        return False

    message = message_from_bytes(raw_email)
    subject = message.get("Subject", "")
    task_id = extract_task_id_from_subject(subject)
    if not task_id:
        return False

    sender_email = extract_sender_email(message.get("From", ""))
    if not sender_email:
        return False

    if sender_email == settings.SMTP_FROM.lower():
        return False

    body = _extract_plain_text(raw_email)
    images = _extract_image_attachments(message)
    if not body and not images:
        return False

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False

    author = get_or_create_user_by_email(db, sender_email)
    comment = TaskComment(
        task_id=task.id,
        author_id=author.id,
        body=body,
        source="email",
        external_message_id=message_id,
    )
    db.add(comment)
    db.flush()

    for image in images:
        try:
            save_attachment_bytes(
                db,
                comment.id,
                image["data"],
                image["filename"],
                image["content_type"],
            )
        except ValueError as exc:
            print(f"Skipped email attachment: {exc}")

    db.add(ProcessedEmail(message_id=message_id))
    db.commit()
    db.refresh(comment)

    assignees = list(task.assignees)
    notify_new_comment(db, task, comment, author, assignees)
    return True


def poll_inbound_emails(db_factory) -> int:
    if not is_imap_configured():
        return 0

    processed_count = 0
    mailbox = None

    try:
        if settings.IMAP_USE_SSL:
            mailbox = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
        else:
            mailbox = imaplib.IMAP4(settings.IMAP_HOST, settings.IMAP_PORT)

        mailbox.login(settings.IMAP_USER, settings.IMAP_PASSWORD)
        mailbox.select(settings.IMAP_FOLDER)

        status, data = mailbox.search(None, "UNSEEN")
        if status != "OK":
            return 0

        message_nums = data[0].split()
        db = db_factory()

        try:
            for num in message_nums[-50:]:
                status, msg_data = mailbox.fetch(num, "(RFC822)")
                if status != "OK" or not msg_data or not msg_data[0]:
                    continue

                raw_email = msg_data[0][1]
                parsed = message_from_bytes(raw_email)
                message_id = parsed.get("Message-ID") or f"{num.decode()}-{time.time()}"

                if process_inbound_email(db, raw_email, message_id):
                    processed_count += 1

                mailbox.store(num, "+FLAGS", "\\Seen")
        finally:
            db.close()
            mailbox.logout()
    except Exception as exc:
        print(f"IMAP poll failed: {exc}")
        try:
            if mailbox is not None:
                mailbox.logout()
        except Exception:
            pass

    return processed_count


_poller_thread: Optional[threading.Thread] = None
_poller_stop = threading.Event()


def _poll_loop(db_factory) -> None:
    while not _poller_stop.is_set():
        try:
            count = poll_inbound_emails(db_factory)
            if count:
                print(f"Processed {count} inbound email comment(s)")
        except Exception as exc:
            print(f"Email poller error: {exc}")
        _poller_stop.wait(settings.EMAIL_POLL_INTERVAL_SECONDS)


def start_email_poller(db_factory) -> None:
    global _poller_thread
    if not settings.EMAIL_ENABLED:
        return
    if _poller_thread and _poller_thread.is_alive():
        return

    _poller_stop.clear()
    _poller_thread = threading.Thread(
        target=_poll_loop,
        args=(db_factory,),
        daemon=True,
        name="email-poller",
    )
    _poller_thread.start()
    print("Email reply poller started")


def stop_email_poller() -> None:
    _poller_stop.set()
