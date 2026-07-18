from __future__ import annotations
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .db import Base, engine
from .observability import record_request
from .routers import (
    analysis,
    audit,
    auth,
    calibrations,
    dashboard,
    health,
    jobs,
    organizations,
    reports,
    reviews,
    sessions,
    subjects,
    templates,
)

s = get_settings()
Base.metadata.create_all(engine)
app = FastAPI(
    title=s.app_name, version="0.1.0", openapi_url="/api/v1/openapi.json", docs_url="/api/docs"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in s.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "Unexpected server error",
                    "request_id": rid,
                }
            },
        )
    duration = time.perf_counter() - start
    record_request(response.status_code, duration)
    response.headers["X-Request-ID"] = rid
    response.headers["X-Process-Time-Ms"] = f"{duration * 1000:.2f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


for router in [
    auth.router,
    organizations.router,
    dashboard.router,
    subjects.router,
    sessions.router,
    jobs.router,
    analysis.router,
    reviews.router,
    reports.router,
    calibrations.router,
    templates.router,
    audit.router,
]:
    app.include_router(router, prefix="/api/v1")
app.include_router(health.router)
