from __future__ import annotations
import gzip
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import tenant_context
from ..models import (
    AnalysisResult,
    GeneratedEvent,
    MediaAsset,
    Membership,
    Session as MovementSession,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _session(session_id: str, org_id: str, db: Session):
    s = db.scalar(
        select(MovementSession).where(
            MovementSession.id == session_id, MovementSession.organization_id == org_id
        )
    )
    if not s:
        raise HTTPException(404, "Session not found")
    return s


@router.get("/{session_id}")
def summary(
    session_id: str, m: Membership = Depends(tenant_context), db: Session = Depends(get_db)
):
    _session(session_id, m.organization_id, db)
    a = db.scalar(
        select(AnalysisResult).where(
            AnalysisResult.session_id == session_id,
            AnalysisResult.organization_id == m.organization_id,
        )
    )
    if not a:
        raise HTTPException(404, "Analysis not found")
    events = db.scalars(
        select(GeneratedEvent).where(
            GeneratedEvent.session_id == session_id,
            GeneratedEvent.organization_id == m.organization_id,
        )
    ).all()
    return {
        "id": a.id,
        "session_id": a.session_id,
        "coordinate_system": a.coordinate_system,
        "unit": a.unit,
        "model_metadata": a.model_metadata,
        "quality_metrics": a.quality_metrics,
        "analytics": a.analytics,
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "severity": e.severity,
                "start_s": e.start_s,
                "end_s": e.end_s,
                "measured_value": e.measured_value,
                "threshold": e.threshold,
                "explanation": e.explanation,
                "review_decision": e.review_decision,
            }
            for e in events
        ],
    }


@router.get("/{session_id}/pose")
def pose(session_id: str, m: Membership = Depends(tenant_context), db: Session = Depends(get_db)):
    _session(session_id, m.organization_id, db)
    a = db.scalar(
        select(AnalysisResult).where(
            AnalysisResult.session_id == session_id,
            AnalysisResult.organization_id == m.organization_id,
        )
    )
    if not a or not Path(a.pose_artifact_key).exists():
        raise HTTPException(404, "Pose artifact not found")
    with gzip.open(a.pose_artifact_key, "rt", encoding="utf-8") as fh:
        return json.load(fh)


@router.get("/{session_id}/evidence")
def evidence(
    session_id: str, m: Membership = Depends(tenant_context), db: Session = Depends(get_db)
):
    _session(session_id, m.organization_id, db)
    a = db.scalar(
        select(AnalysisResult).where(
            AnalysisResult.session_id == session_id,
            AnalysisResult.organization_id == m.organization_id,
        )
    )
    if not a or not a.evidence_key or not Path(a.evidence_key).exists():
        raise HTTPException(404, "Evidence not found")
    return FileResponse(
        a.evidence_key, media_type="image/jpeg", filename=f"{session_id}-evidence.jpg"
    )


@router.get("/{session_id}/source")
def source_video(
    session_id: str, m: Membership = Depends(tenant_context), db: Session = Depends(get_db)
):
    _session(session_id, m.organization_id, db)
    media = db.scalar(
        select(MediaAsset)
        .where(
            MediaAsset.session_id == session_id,
            MediaAsset.organization_id == m.organization_id,
            MediaAsset.kind == "source_video",
        )
        .order_by(MediaAsset.created_at.desc())
    )
    if not media or not Path(media.storage_key).exists():
        raise HTTPException(404, "Source video not found")
    return FileResponse(
        media.storage_key,
        media_type=media.mime_type,
        filename=f"{session_id}-source{Path(media.storage_key).suffix}",
    )
