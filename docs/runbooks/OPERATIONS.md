# Operations Runbook

## Stuck queued jobs

- Check Redis connectivity and Celery worker health.
- Inspect the persisted job stage and attempts.
- Confirm the worker can read the model and storage volumes.
- Retry only when the job is not terminal and no active worker owns it.

## No person detected

- Confirm model backend is `movenet`, not the controlled marker adapter.
- Review evidence/input orientation, lighting, full-body visibility, and sampling rate.
- Raise inference resolution or sampled FPS only after CPU/memory review.

## High reprojection error

- Verify camera intrinsics match resolution and focus.
- Re-run calibration with broader board coverage.
- Confirm synchronized timestamps and correct camera ordering.
- Reject metric interpretation until error returns below policy threshold.

## Storage failure

- Leave the job failed; do not report completion.
- Verify free space, permissions, bucket policy, and credentials.
- Remove orphan temporary files after identifying the failure reference ID.

## Database migration failure

- Stop rollout.
- Back up the database.
- Read the failed revision and SQL error.
- Repair or restore before restarting API/worker replicas.
