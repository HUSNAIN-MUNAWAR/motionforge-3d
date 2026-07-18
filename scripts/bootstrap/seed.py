from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "apps/api")]
from motionforge.db import Base, SessionLocal, engine
from motionforge.models import Membership, Organization, Session, Subject, User
from motionforge.security import hash_password

Base.metadata.create_all(engine)
with SessionLocal() as db:
    if db.query(User).filter_by(email="demo@motionforge.local").first():
        print("Seed already exists")
        raise SystemExit
    owner = User(
        email="demo@motionforge.local",
        display_name="Demo Owner",
        password_hash=hash_password("MotionForgeDemo!2026"),
    )
    reviewer = User(
        email="reviewer@motionforge.local",
        display_name="Demo Reviewer",
        password_hash=hash_password("MotionForgeReview!2026"),
    )
    org = Organization(name="MotionForge Lab", slug="motionforge-lab")
    db.add_all([owner, reviewer, org])
    db.flush()
    db.add_all(
        [
            Membership(organization_id=org.id, user_id=owner.id, role="owner"),
            Membership(organization_id=org.id, user_id=reviewer.id, role="reviewer"),
        ]
    )
    subjects = []
    for code in ["ATH-001", "ERG-014", "GAIT-008"]:
        s = Subject(
            organization_id=org.id,
            display_name=code,
            external_reference=code,
            consent_status="recorded",
            created_by=owner.id,
            tags=["seeded-synthetic"],
        )
        db.add(s)
        subjects.append(s)
    db.flush()
    db.add_all(
        [
            Session(
                organization_id=org.id,
                subject_id=subjects[0].id,
                title="Squat baseline — seeded",
                movement_template="squat",
                status="completed",
                review_status="approved_with_notes",
                created_by=owner.id,
            ),
            Session(
                organization_id=org.id,
                subject_id=subjects[1].id,
                title="Shoulder raise — seeded",
                movement_template="shoulder_raise",
                status="completed",
                review_status="in_review",
                created_by=owner.id,
            ),
            Session(
                organization_id=org.id,
                subject_id=subjects[2].id,
                title="Walk capture — seeded failure",
                movement_template="sit_to_stand",
                status="failed",
                review_status="needs_recapture",
                created_by=owner.id,
            ),
        ]
    )
    db.commit()
    print("Seeded demo@motionforge.local / MotionForgeDemo!2026")
