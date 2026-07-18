from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import current_user, tenant_context
from ..models import (
    MediaAsset,
    Membership,
    ProcessingJob,
    Session as MovementSession,
    Subject,
    User,
)
from ..schemas import JobOut, SessionIn, SessionOut
from ..services.audit import audit
from ..services.storage import save_upload

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=201)
def create(
    data: SessionIn,
    m: Membership = Depends(tenant_context),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    subject = db.scalar(
        select(Subject).where(
            Subject.id == data.subject_id, Subject.organization_id == m.organization_id
        )
    )
    if not subject:
        raise HTTPException(404, "Subject not found")
    s = MovementSession(organization_id=m.organization_id, created_by=user.id, **data.model_dump())
    db.add(s)
    audit(db, "session.created", "session", s.id, m.organization_id, user.id)
    db.commit()
    db.refresh(s)
    return s


@router.get("", response_model=list[SessionOut])
def list_sessions(m: Membership = Depends(tenant_context), db: Session = Depends(get_db)):
    return db.scalars(
        select(MovementSession)
        .where(MovementSession.organization_id == m.organization_id)
        .order_by(MovementSession.created_at.desc())
    ).all()


@router.get("/{session_id}", response_model=SessionOut)
def get_session(
    session_id: str, m: Membership = Depends(tenant_context), db: Session = Depends(get_db)
):
    s = db.scalar(
        select(MovementSession).where(
            MovementSession.id == session_id, MovementSession.organization_id == m.organization_id
        )
    )
    if not s:
        raise HTTPException(404, "Session not found")
    return s


@router.post("/{session_id}/media", response_model=JobOut, status_code=202)
def upload(
    session_id: str,
    file: UploadFile = File(...),
    m: Membership = Depends(tenant_context),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    session = db.scalar(
        select(MovementSession).where(
            MovementSession.id == session_id, MovementSession.organization_id == m.organization_id
        )
    )
    if not session:
        raise HTTPException(404, "Session not found")
    try:
        path, meta = save_upload(file, m.organization_id, session_id)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    duplicate = db.scalar(
        select(MediaAsset).where(
            MediaAsset.organization_id == m.organization_id, MediaAsset.sha256 == meta["sha256"]
        )
    )
    if duplicate:
        path.unlink(missing_ok=True)
        raise HTTPException(
            409,
            detail={
                "message": "Duplicate media already exists in this organization",
                "media_asset_id": duplicate.id,
            },
        )
    media = MediaAsset(
        organization_id=m.organization_id,
        session_id=session.id,
        storage_key=str(path),
        original_filename=Path(file.filename or "video").name,
        mime_type=file.content_type or "application/octet-stream",
        metadata_json={},
        **meta,
    )
    db.add(media)
    db.flush()
    job = ProcessingJob(
        organization_id=m.organization_id,
        session_id=session.id,
        media_asset_id=media.id,
        state="queued",
        stage="queued",
        progress=0,
    )
    db.add(job)
    session.status = "queued"
    audit(
        db,
        "media.uploaded",
        "media",
        media.id,
        m.organization_id,
        user.id,
        {"sha256": media.sha256, "size_bytes": media.size_bytes},
    )
    db.commit()
    db.refresh(job)
    from ..config import get_settings

    if get_settings().queue_mode == "celery":
        from apps.worker.tasks import process_job

        process_job.delay(job.id)
    return job
