from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import require_roles
from ..models import AuditEvent, Membership

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
def list_audit_events(
    limit: int = Query(100, ge=1, le=500),
    membership: Membership = Depends(require_roles("owner", "admin", "reviewer")),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = db.scalars(
        select(AuditEvent)
        .where(AuditEvent.organization_id == membership.organization_id)
        .order_by(AuditEvent.created_at.desc())
        .limit(limit)
    ).all()
    return [
        {
            "id": row.id,
            "action": row.action,
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "actor_id": row.actor_id,
            "metadata": row.metadata_json,
            "created_at": row.created_at,
        }
        for row in rows
    ]
