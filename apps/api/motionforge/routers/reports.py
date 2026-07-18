from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import current_user, tenant_context
from ..models import Membership, Report, Session as MovementSession, User
from ..services.audit import audit
from ..services.reporting import generate_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/sessions/{session_id}", status_code=201)
def create(
    session_id: str,
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
        r = generate_report(db, session, user.id)
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    audit(db, "report.generated", "report", r.id, m.organization_id, user.id)
    db.commit()
    return {"id": r.id, "status": r.status}


@router.get("/{report_id}/download")
def download(
    report_id: str, m: Membership = Depends(tenant_context), db: Session = Depends(get_db)
):
    r = db.scalar(
        select(Report).where(Report.id == report_id, Report.organization_id == m.organization_id)
    )
    if not r or not Path(r.storage_key).exists():
        raise HTTPException(404, "Report not found")
    return FileResponse(
        r.storage_key, media_type="application/pdf", filename=f"motionforge-{r.session_id}.pdf"
    )
