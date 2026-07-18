from sqlalchemy.orm import Session
from ..models import AuditEvent


def audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str | None,
    organization_id: str | None,
    actor_id: str | None,
    metadata: dict | None = None,
):
    db.add(
        AuditEvent(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            organization_id=organization_id,
            actor_id=actor_id,
            metadata_json=metadata or {},
        )
    )
