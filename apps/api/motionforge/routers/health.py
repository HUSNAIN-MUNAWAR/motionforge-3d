from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from sqlalchemy import text
from ..db import SessionLocal
from ..observability import prometheus_text

router = APIRouter(tags=["operations"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "motionforge-api"}


@router.get("/ready")
def ready():
    with SessionLocal() as db:
        db.execute(text("select 1"))
    return {"status": "ready"}


@router.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    return prometheus_text()
