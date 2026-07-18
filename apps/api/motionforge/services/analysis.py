from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from packages.motion_analytics import analyze, load_template
from packages.pose_core import ColorMarkerPoseEstimator, MoveNetONNXPoseEstimator, process_video
from ..config import get_settings
from ..models import (
    AnalysisResult,
    GeneratedEvent,
    MediaAsset,
    ProcessingJob,
    Session as MovementSession,
)


def _estimator():
    s = get_settings()
    if s.model_backend == "movenet":
        return MoveNetONNXPoseEstimator(s.model_path)
    if s.model_backend == "marker":
        return ColorMarkerPoseEstimator()
    raise ValueError(f"Unsupported model backend: {s.model_backend}")


def run_job(db: Session, job_id: str) -> AnalysisResult:
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise KeyError(job_id)
    session = db.get(MovementSession, job.session_id)
    media = db.get(MediaAsset, job.media_asset_id)
    if not session or not media:
        raise RuntimeError("Job references missing session or media")
    if job.state == "completed":
        existing = db.scalar(select(AnalysisResult).where(AnalysisResult.session_id == session.id))
        if existing:
            return existing
    job.state = "active"
    job.stage = "validating"
    job.progress = 2
    job.attempts += 1
    job.started_at = datetime.now(timezone.utc)
    session.status = "processing"
    db.commit()

    def progress(value: int, stage: str):
        job.progress = value
        job.stage = stage
        db.commit()

    try:
        artifact_dir = get_settings().storage_root / "artifacts" / job.organization_id / session.id
        estimator = _estimator()
        result = process_video(
            media.storage_key,
            estimator,
            session.id,
            artifact_dir,
            sample_fps=float(
                session.processing_configuration.get("sample_fps", get_settings().sample_fps)
            ),
            progress=progress,
        )
        progress(82, "calculating_metrics")
        template = load_template(session.movement_template)
        analytics = analyze(result["filtered"], template)
        progress(90, "persisting_results")
        existing = db.scalar(select(AnalysisResult).where(AnalysisResult.session_id == session.id))
        if existing:
            db.delete(existing)
            db.flush()
        db.execute(delete(GeneratedEvent).where(GeneratedEvent.session_id == session.id))
        ar = AnalysisResult(
            organization_id=job.organization_id,
            session_id=session.id,
            pose_artifact_key=result["pose_path"],
            evidence_key=result["evidence_path"],
            model_metadata={
                "name": estimator.metadata.name,
                "version": estimator.metadata.version,
                "runtime": estimator.metadata.runtime,
                "input_size": estimator.metadata.input_size,
                "model_hash": estimator.metadata.model_hash,
                "notes": estimator.metadata.notes,
            },
            quality_metrics=result["quality"],
            analytics=analytics,
        )
        db.add(ar)
        db.flush()
        for event in analytics["events"]:
            db.add(
                GeneratedEvent(
                    organization_id=job.organization_id,
                    session_id=session.id,
                    event_type=event["event_type"],
                    severity=event["severity"],
                    start_s=event["start_s"],
                    end_s=event["end_s"],
                    body_side=event.get("side"),
                    joint=event.get("joint"),
                    measured_value=event["measured_value"],
                    threshold=event["threshold"],
                    unit=event["unit"],
                    confidence=event["confidence"],
                    explanation=event["explanation"],
                    rule_version=event["rule_version"],
                )
            )
        job.progress = 100
        job.stage = "completed"
        job.state = "completed"
        job.completed_at = datetime.now(timezone.utc)
        session.status = "completed"
        db.commit()
        db.refresh(ar)
        return ar
    except Exception as exc:
        job.state = "failed"
        job.stage = "failed"
        job.error_code = type(exc).__name__
        job.error_message = str(exc)[:2000]
        session.status = "failed"
        db.commit()
        raise
