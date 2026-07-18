from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import current_user
from ..models import Membership, Organization, User
from ..schemas import OrganizationIn, OrganizationOut
from ..services.audit import audit

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationOut, status_code=201)
def create(data: OrganizationIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if db.scalar(select(Organization).where(Organization.slug == data.slug)):
        raise HTTPException(409, "Slug already exists")
    org = Organization(name=data.name, slug=data.slug)
    db.add(org)
    db.flush()
    db.add(Membership(organization_id=org.id, user_id=user.id, role="owner"))
    audit(db, "organization.created", "organization", org.id, org.id, user.id)
    db.commit()
    db.refresh(org)
    return org


@router.get("", response_model=list[OrganizationOut])
def list_orgs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Organization)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Membership.user_id == user.id)
    ).all()
