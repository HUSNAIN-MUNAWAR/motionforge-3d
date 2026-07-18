from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import current_user, require_roles, tenant_context
from ..models import Membership, ProcessingJob, User
from ..schemas import JobOut
from ..services.analysis import run_job
from ..services.audit import audit

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobOut)
def get(job_id: str, m: Membership = Depends(tenant_context), db: Session = Depends(get_db)):
    job = db.scalar(
        select(ProcessingJob).where(
            ProcessingJob.id == job_id, ProcessingJob.organization_id == m.organization_id
        )
    )
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.post("/{job_id}/run", response_model=JobOut)
def run(
    job_id: str,
    m: Membership = Depends(require_roles("owner", "administrator", "analyst", "coach")),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    job = db.scalar(
        select(ProcessingJob).where(
            ProcessingJob.id == job_id, ProcessingJob.organization_id == m.organization_id
        )
    )
    if not job:
        raise HTTPException(404, "Job not found")
    try:
        run_job(db, job.id)
    except Exception as exc:
        raise HTTPException(
            422,
            detail={
                "message": "Processing failed",
                "reference": job.id,
                "stage": job.stage,
                "reason": str(exc),
            },
        )
    audit(db, "job.completed", "processing_job", job.id, m.organization_id, user.id)
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/cancel", response_model=JobOut)
def cancel(
    job_id: str,
    m: Membership = Depends(tenant_context),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    job = db.scalar(
        select(ProcessingJob).where(
            ProcessingJob.id == job_id, ProcessingJob.organization_id == m.organization_id
        )
    )
    if not job:
        raise HTTPException(404, "Job not found")
    if job.state in {"completed", "failed", "cancelled"}:
        raise HTTPException(409, "Job is already terminal")
    job.cancellation_requested = True
    job.state = "cancelled"
    job.stage = "cancelled"
    audit(db, "job.cancelled", "processing_job", job.id, m.organization_id, user.id)
    db.commit()
    db.refresh(job)
    return job
