from __future__ import annotations
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import get_db
from .models import Membership, User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(401, "Authentication required")
    try:
        uid = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, uid)
    if not user or not user.is_active:
        raise HTTPException(401, "Inactive user")
    return user


def tenant_context(
    x_organization_id: str = Header(..., alias="X-Organization-ID"),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Membership:
    membership = db.scalar(
        select(Membership).where(
            Membership.organization_id == x_organization_id, Membership.user_id == user.id
        )
    )
    if not membership:
        raise HTTPException(403, "Organization access denied")
    return membership


def require_roles(*roles):
    def dependency(m: Membership = Depends(tenant_context)):
        if m.role not in roles:
            raise HTTPException(403, "Insufficient role")
        return m

    return dependency
