from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import tenant_context
from ..models import AnalysisResult, GeneratedEvent, Membership, ProcessingJob
from ..models import Session as MovementSession
from ..models import Subject

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(
    membership: Membership = Depends(tenant_context), db: Session = Depends(get_db)
) -> dict:
    org_id = membership.organization_id
    sessions_total = (
        db.scalar(
            select(func.count())
            .select_from(MovementSession)
            .where(MovementSession.organization_id == org_id)
        )
        or 0
    )
    subjects_total = (
        db.scalar(
            select(func.count()).select_from(Subject).where(Subject.organization_id == org_id)
        )
        or 0
    )
    jobs_active = (
        db.scalar(
            select(func.count())
            .select_from(ProcessingJob)
            .where(
                ProcessingJob.organization_id == org_id,
                ProcessingJob.state.in_(["pending", "queued", "active"]),
            )
        )
        or 0
    )
    jobs_failed = (
        db.scalar(
            select(func.count())
            .select_from(ProcessingJob)
            .where(ProcessingJob.organization_id == org_id, ProcessingJob.state == "failed")
        )
        or 0
    )
    awaiting_review = (
        db.scalar(
            select(func.count())
            .select_from(MovementSession)
            .where(
                MovementSession.organization_id == org_id,
                MovementSession.status == "completed",
                MovementSession.review_status.in_(["not_reviewed", "in_review"]),
            )
        )
        or 0
    )
    completed = (
        db.scalar(
            select(func.count())
            .select_from(MovementSession)
            .where(MovementSession.organization_id == org_id, MovementSession.status == "completed")
        )
        or 0
    )
    severity_rows = db.execute(
        select(GeneratedEvent.severity, func.count(GeneratedEvent.id))
        .where(GeneratedEvent.organization_id == org_id)
        .group_by(GeneratedEvent.severity)
    ).all()
    severities: dict[str, int] = {str(severity): int(count) for severity, count in severity_rows}
    confidence_rows = db.scalars(
        select(AnalysisResult).where(AnalysisResult.organization_id == org_id)
    ).all()
    confidence_values = [
        float(row.quality_metrics.get("average_landmark_confidence", 0.0))
        for row in confidence_rows
        if row.quality_metrics
    ]
    return {
        "sessions_total": sessions_total,
        "subjects_total": subjects_total,
        "completed_sessions": completed,
        "awaiting_review": awaiting_review,
        "active_jobs": jobs_active,
        "failed_jobs": jobs_failed,
        "average_analysis_confidence": round(sum(confidence_values) / len(confidence_values), 4)
        if confidence_values
        else None,
        "events_by_severity": severities,
    }
