from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


def uid():
    return str(uuid4())


def now():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)


class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("organization_id", "user_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(40), default="viewer")


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    display_name: Mapped[str] = mapped_column(String(160))
    external_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    year_of_birth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    dominant_side: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    consent_status: Mapped[str] = mapped_column(String(30), default="not_recorded")
    consent_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    retention_classification: Mapped[str] = mapped_column(String(40), default="standard")
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))


class Session(Base, TimestampMixin):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    movement_template: Mapped[str] = mapped_column(String(60))
    capture_type: Mapped[str] = mapped_column(String(40), default="single_video")
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    review_status: Mapped[str] = mapped_column(String(40), default="not_reviewed")
    recording_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    environment: Mapped[dict] = mapped_column(JSON, default=dict)
    camera_configuration: Mapped[dict] = mapped_column(JSON, default=dict)
    model_configuration: Mapped[dict] = mapped_column(JSON, default=dict)
    processing_configuration: Mapped[dict] = mapped_column(JSON, default=dict)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    assigned_reviewer: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class MediaAsset(Base, TimestampMixin):
    __tablename__ = "media_assets"
    __table_args__ = (UniqueConstraint("organization_id", "sha256"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    kind: Mapped[str] = mapped_column(String(40), default="source_video")
    storage_key: Mapped[str] = mapped_column(String(500))
    original_filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    size_bytes: Mapped[int] = mapped_column(Integer)
    duration_s: Mapped[float] = mapped_column(Float)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    fps: Mapped[float] = mapped_column(Float)
    codec: Mapped[str] = mapped_column(String(80))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class ProcessingJob(Base, TimestampMixin):
    __tablename__ = "processing_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    media_asset_id: Mapped[str] = mapped_column(ForeignKey("media_assets.id"))
    state: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    stage: Mapped[str] = mapped_column(String(80), default="pending")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AnalysisResult(Base, TimestampMixin):
    __tablename__ = "analysis_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), unique=True, index=True)
    pose_artifact_key: Mapped[str] = mapped_column(String(500))
    evidence_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    model_metadata: Mapped[dict] = mapped_column(JSON)
    quality_metrics: Mapped[dict] = mapped_column(JSON)
    analytics: Mapped[dict] = mapped_column(JSON)
    coordinate_system: Mapped[str] = mapped_column(String(50), default="camera_plane_3d")
    unit: Mapped[str] = mapped_column(String(30), default="normalized")


class GeneratedEvent(Base, TimestampMixin):
    __tablename__ = "generated_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    severity: Mapped[str] = mapped_column(String(30))
    start_s: Mapped[float] = mapped_column(Float)
    end_s: Mapped[float] = mapped_column(Float)
    body_side: Mapped[str | None] = mapped_column(String(20), nullable=True)
    joint: Mapped[str | None] = mapped_column(String(50), nullable=True)
    measured_value: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30))
    confidence: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(Text)
    rule_version: Mapped[str] = mapped_column(String(30))
    machine_status: Mapped[str] = mapped_column(String(30), default="generated")
    review_decision: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class ReviewAnnotation(Base, TimestampMixin):
    __tablename__ = "review_annotations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    event_id: Mapped[str | None] = mapped_column(ForeignKey("generated_events.id"), nullable=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    timestamp_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    note: Mapped[str] = mapped_column(Text)
    annotation_type: Mapped[str] = mapped_column(String(40), default="note")


class CameraCalibration(Base, TimestampMixin):
    __tablename__ = "camera_calibrations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    method: Mapped[str] = mapped_column(String(40))
    parameters: Mapped[dict] = mapped_column(JSON)
    reprojection_error: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="valid")


class Report(Base, TimestampMixin):
    __tablename__ = "reports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    storage_key: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="completed")
    generated_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    report_version: Mapped[str] = mapped_column(String(20), default="1.0")


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(60))
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
