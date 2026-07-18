from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from packages.motion_analytics.templates import load_template

from ..deps import tenant_context
from ..models import Membership

router = APIRouter(prefix="/movement-templates", tags=["movement-templates"])
NAMES = ["squat", "bicep_curl", "shoulder_raise", "sit_to_stand"]


@router.get("")
def list_templates(_: Membership = Depends(tenant_context)) -> list[dict]:
    return [load_template(name) for name in NAMES]


@router.get("/{name}")
def get_template(name: str, _: Membership = Depends(tenant_context)) -> dict:
    if name not in NAMES:
        raise HTTPException(404, "Movement template not found")
    return load_template(name)
