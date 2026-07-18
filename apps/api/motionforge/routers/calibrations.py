from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import current_user, tenant_context
from ..models import CameraCalibration, Membership, User
from ..services.audit import audit

router = APIRouter(prefix="/calibrations", tags=["calibrations"])


class CalibrationIn(BaseModel):
    name: str
    method: str = Field(pattern=r"^(chessboard|charuco|imported)$")
    parameters: dict
    reprojection_error: float = Field(ge=0)


@router.post("", status_code=201)
def create(
    data: CalibrationIn,
    m: Membership = Depends(tenant_context),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    c = CameraCalibration(
        organization_id=m.organization_id,
        status="valid" if data.reprojection_error < 2 else "warning",
        **data.model_dump(),
    )
    db.add(c)
    audit(db, "calibration.created", "camera_calibration", c.id, m.organization_id, user.id)
    db.commit()
    db.refresh(c)
    return c


@router.get("")
def list_all(m: Membership = Depends(tenant_context), db: Session = Depends(get_db)):
    return db.scalars(
        select(CameraCalibration).where(CameraCalibration.organization_id == m.organization_id)
    ).all()
