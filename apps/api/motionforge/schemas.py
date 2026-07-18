from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10)
    display_name: str = Field(min_length=2, max_length=120)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(ORM):
    id: str
    email: str
    display_name: str


class OrganizationIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    slug: str = Field(pattern=r"^[a-z0-9-]+$")


class OrganizationOut(ORM):
    id: str
    name: str
    slug: str
    created_at: datetime


class SubjectIn(BaseModel):
    display_name: str
    external_reference: str | None = None
    year_of_birth: int | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    dominant_side: str | None = None
    tags: list[str] = []
    notes: str | None = None
    consent_status: str = "not_recorded"
    retention_classification: str = "standard"


class SubjectOut(ORM):
    id: str
    organization_id: str
    display_name: str
    external_reference: str | None
    tags: list
    consent_status: str
    archived: bool
    created_at: datetime


class SessionIn(BaseModel):
    subject_id: str
    title: str
    movement_template: str
    notes: str | None = None
    processing_configuration: dict = {}


class SessionOut(ORM):
    id: str
    organization_id: str
    subject_id: str
    title: str
    movement_template: str
    status: str
    review_status: str
    created_at: datetime


class JobOut(ORM):
    id: str
    session_id: str
    state: str
    stage: str
    progress: int
    error_code: str | None
    error_message: str | None


class AnnotationIn(BaseModel):
    note: str = Field(min_length=1, max_length=5000)
    timestamp_s: float | None = None
    event_id: str | None = None
    annotation_type: str = "note"


class EventReviewIn(BaseModel):
    decision: str = Field(pattern=r"^(confirmed|rejected)$")
    reason: str = Field(min_length=2, max_length=2000)
