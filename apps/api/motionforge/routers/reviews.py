from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import current_user, tenant_context
from ..models import GeneratedEvent, Membership, ReviewAnnotation, Session as MovementSession, User
from ..schemas import AnnotationIn, EventReviewIn
from ..services.audit import audit

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/sessions/{session_id}/annotations", status_code=201)
def annotate(
    session_id: str,
    data: AnnotationIn,
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
    if data.event_id:
        event = db.scalar(
            select(GeneratedEvent).where(
                GeneratedEvent.id == data.event_id,
                GeneratedEvent.organization_id == m.organization_id,
                GeneratedEvent.session_id == session_id,
            )
        )
        if not event:
            raise HTTPException(404, "Event not found")
    note = ReviewAnnotation(
        organization_id=m.organization_id,
        session_id=session_id,
        author_id=user.id,
        **data.model_dump(),
    )
    db.add(note)
    audit(db, "review.annotation_added", "review_annotation", note.id, m.organization_id, user.id)
    db.commit()
    db.refresh(note)
    return {"id": note.id, "created_at": note.created_at}


@router.post("/events/{event_id}")
def review_event(
    event_id: str,
    data: EventReviewIn,
    m: Membership = Depends(tenant_context),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    event = db.scalar(
        select(GeneratedEvent).where(
            GeneratedEvent.id == event_id, GeneratedEvent.organization_id == m.organization_id
        )
    )
    if not event:
        raise HTTPException(404, "Event not found")
    event.review_decision = data.decision
    event.review_reason = data.reason
    event.reviewed_by = user.id
    audit(
        db,
        "event.reviewed",
        "generated_event",
        event.id,
        m.organization_id,
        user.id,
        {"decision": data.decision, "original_machine_status": event.machine_status},
    )
    db.commit()
    return {"id": event.id, "decision": event.review_decision}
