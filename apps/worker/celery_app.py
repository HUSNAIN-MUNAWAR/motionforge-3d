from celery import Celery
from motionforge.config import get_settings

s = get_settings()
celery_app = Celery(
    "motionforge",
    broker=s.celery_broker_url,
    backend=s.celery_result_backend,
    include=["apps.worker.tasks"],
)
celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)
