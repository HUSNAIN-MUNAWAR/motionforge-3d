from apps.worker.celery_app import celery_app
from motionforge.db import SessionLocal
from motionforge.services.analysis import run_job


@celery_app.task(bind=True, autoretry_for=(OSError,), retry_backoff=True, max_retries=3)
def process_job(self, job_id: str):
    with SessionLocal() as db:
        result = run_job(db, job_id)
        return {"analysis_result_id": result.id, "session_id": result.session_id}
