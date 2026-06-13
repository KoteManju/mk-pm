# Task management routes
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import (
    Task as TaskModel,
    User as UserModel,
    TaskComment as TaskCommentModel,
    CommentAttachment as CommentAttachmentModel,
)
from app.schemas import Task, TaskCreate, TaskUpdate, TaskComment
from app.services.email_service import (
    resolve_assignees,
    notify_assignment,
    notify_new_comment,
)
from app.services.attachment_service import (
    save_upload_files,
    get_attachment_file_path,
)

router = APIRouter()


def _task_query(db: Session):
    return db.query(TaskModel).options(
        joinedload(TaskModel.assignees),
        joinedload(TaskModel.comments).joinedload(TaskCommentModel.author),
    )


def _comment_query(db: Session):
    return db.query(TaskCommentModel).options(
        joinedload(TaskCommentModel.author),
        joinedload(TaskCommentModel.attachments),
    )


def _apply_assignees(
    db: Session,
    task: TaskModel,
    assignee_ids: Optional[List[int]] = None,
    assignee_emails: Optional[List[str]] = None,
    notify: bool = True,
    assigned_by: Optional[str] = None,
) -> None:
    previous_ids = {user.id for user in task.assignees}

    try:
        users = resolve_assignees(db, assignee_ids=assignee_ids, assignee_emails=assignee_emails)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    task.assignees = users
    task.assignee_id = users[0].id if users else None

    if notify:
        for user in users:
            if user.id not in previous_ids:
                notify_assignment(db, task, user, assigned_by=assigned_by)


def _extract_assignee_fields(data: dict):
    assignee_ids = data.pop("assignee_ids", None)
    assignee_emails = data.pop("assignee_emails", None)
    return assignee_ids, assignee_emails


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    try:
        task_data = task.model_dump(exclude={"assignee_ids", "assignee_emails"})
        db_task = TaskModel(**task_data)
        db.add(db_task)
        db.flush()

        _apply_assignees(
            db,
            db_task,
            assignee_ids=task.assignee_ids,
            assignee_emails=task.assignee_emails,
            notify=True,
        )
        db.commit()
        db_task = _task_query(db).filter(TaskModel.id == db_task.id).first()
        return db_task
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    project_id: int = None,
    db: Session = Depends(get_db),
):
    query = _task_query(db)
    if project_id:
        query = query.filter(TaskModel.project_id == project_id)
    return query.offset(skip).limit(limit).all()


@router.get("/attachments/{attachment_id}")
def get_comment_attachment(attachment_id: int, db: Session = Depends(get_db)):
    attachment = db.query(CommentAttachmentModel).filter(CommentAttachmentModel.id == attachment_id).first()
    if attachment is None:
        raise HTTPException(status_code=404, detail="Attachment not found")

    file_path = get_attachment_file_path(attachment)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Attachment file missing")

    return FileResponse(
        path=file_path,
        media_type=attachment.content_type,
        filename=attachment.filename,
    )


@router.get("/{task_id}", response_model=Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = _task_query(db).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db_task = db.query(TaskModel).options(joinedload(TaskModel.assignees)).filter(TaskModel.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task.model_dump(exclude_unset=True)
    assignee_ids, assignee_emails = _extract_assignee_fields(update_data)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    if assignee_ids is not None or assignee_emails is not None:
        _apply_assignees(
            db,
            db_task,
            assignee_ids=assignee_ids or [],
            assignee_emails=assignee_emails or [],
            notify=True,
            assigned_by=current_user.full_name or current_user.username,
        )

    db.commit()
    db_task = _task_query(db).filter(TaskModel.id == task_id).first()
    return db_task


@router.get("/{task_id}/comments", response_model=List[TaskComment])
def read_task_comments(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return (
        _comment_query(db)
        .filter(TaskCommentModel.task_id == task_id)
        .order_by(TaskCommentModel.created_at.asc())
        .all()
    )


@router.post("/{task_id}/comments", response_model=TaskComment, status_code=status.HTTP_201_CREATED)
async def create_task_comment(
    task_id: int,
    body: str = Form(""),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = (
        db.query(TaskModel)
        .options(joinedload(TaskModel.assignees))
        .filter(TaskModel.id == task_id)
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    text = body.strip()
    uploads = [upload for upload in files if upload.filename]
    if not text and not uploads:
        raise HTTPException(status_code=400, detail="Comment text or image attachment is required")

    db_comment = TaskCommentModel(
        task_id=task_id,
        author_id=current_user.id,
        body=text,
        source="app",
    )
    db.add(db_comment)
    db.flush()

    try:
        await save_upload_files(db, db_comment.id, uploads)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.commit()

    db_comment = _comment_query(db).filter(TaskCommentModel.id == db_comment.id).first()
    notify_new_comment(db, task, db_comment, current_user, list(task.assignees))
    return db_comment
