from __future__ import annotations
import argparse
import time
from sqlalchemy import select
from motionforge.db import SessionLocal
from motionforge.models import ProcessingJob
from motionforge.services.analysis import run_job


def work_once() -> bool:
    with SessionLocal() as db:
        job = db.scalar(
            select(ProcessingJob)
            .where(ProcessingJob.state == "queued")
            .order_by(ProcessingJob.created_at)
            .limit(1)
        )
        if not job:
            return False
        try:
            run_job(db, job.id)
        except Exception as exc:
            print(f"job {job.id} failed: {exc}")
        return True


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true")
    p.add_argument("--interval", type=float, default=2)
    a = p.parse_args()
    if a.once:
        work_once()
    else:
        while True:
            if not work_once():
                time.sleep(a.interval)
