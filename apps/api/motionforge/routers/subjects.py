from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import current_user, tenant_context
from ..models import Membership, Subject, User
from ..schemas import SubjectIn, SubjectOut
from ..services.audit import audit

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("", response_model=SubjectOut, status_code=201)
def create(
    data: SubjectIn,
    m: Membership = Depends(tenant_context),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    subject = Subject(organization_id=m.organization_id, created_by=user.id, **data.model_dump())
    db.add(subject)
    audit(db, "subject.created", "subject", subject.id, m.organization_id, user.id)
    db.commit()
    db.refresh(subject)
    return subject


@router.get("", response_model=list[SubjectOut])
def list_subjects(
    q: str | None = Query(None),
    m: Membership = Depends(tenant_context),
    db: Session = Depends(get_db),
):
    stmt = select(Subject).where(
        Subject.organization_id == m.organization_id, Subject.archived.is_(False)
    )
    if q:
        stmt = stmt.where(Subject.display_name.ilike(f"%{q}%"))
    return db.scalars(stmt.order_by(Subject.created_at.desc())).all()


@router.get("/{subject_id}", response_model=SubjectOut)
def get(subject_id: str, m: Membership = Depends(tenant_context), db: Session = Depends(get_db)):
    s = db.scalar(
        select(Subject).where(
            Subject.id == subject_id, Subject.organization_id == m.organization_id
        )
    )
    if not s:
        raise HTTPException(404, "Subject not found")
    return s
