# Verification Report

**Verification date:** 2026-07-19
**Repository version:** 0.1.0

## Environment

- Operating system: `Linux-4.4.0-x86_64-with-glibc2.41`
- Python: `3.13.5`
- Node: `v22.16.0`
- npm: `10.9.2`
- Docker: unavailable in the execution sandbox
- FFmpeg: `7.1.3`
- OpenCV: `4.13.0`
- Execution profile: CPU-only sandbox

## Commands executed

```bash
ruff format apps packages scripts tests
ruff check apps packages scripts tests
mypy apps/api packages scripts
PYTHONPATH=.:apps/api pytest -q
PYTHONPATH=.:apps/api python scripts/verification/verify_e2e.py
cd apps/web && npm run typecheck && npm run build
MOTIONFORGE_DATABASE_URL=sqlite:///./migration_test.db \
  PYTHONPATH=.:apps/api alembic upgrade head
PYTHONPATH=.:apps/api python -m compileall -q apps packages scripts tests
```

## Quality gates

- Ruff formatting: **passed**
- Ruff lint: **passed**
- MyPy: **passed across 52 Python source files**
- Pytest: **9 passed**
- Python compile-all: **passed**
- Next.js TypeScript validation: **passed**
- Next.js optimized production build: **passed**
- Alembic clean-database migration: **passed**
- Migrated SQLite schema: **14 tables**, including `sessions`, `analysis_results`, and `alembic_version`

The automated tests cover authentication, cross-tenant access denial, subject creation, joint-angle geometry, degenerate vectors, timestamp-aware derivatives, symmetry, EMA, One Euro filtering, repetition detection, known-camera triangulation, and reprojection error.

## Measured encoded-video workflow

- Job state: **completed**
- Video: `tests/fixtures/controlled_squat.mp4`
- Frames decoded: **96**
- Frames sampled/analyzed: **32**
- Valid pose frames: **32**
- Average landmark confidence: **1.0**
- Pose estimator executed: **opencv-color-fiducial-pose**
- Measured pipeline and report duration: **30.894 seconds**
- Repetitions detected: **2**
- Generated events: **0**
- Explainable score: **84.52**

The executed estimator is the controlled OpenCV color-fiducial adapter. It recovered keypoints from encoded MP4 pixels and did not read fixture coordinates directly. It is a deterministic verification and calibration adapter, not the production general-human model.

## Packaged verification artifacts

- Pose sequence: `docs/verification_artifacts/pose_sequence.json.gz`
- Evidence frame: `docs/verification_artifacts/evidence.jpg`
- PDF report: `docs/verification_artifacts/analysis_report.pdf`
- Machine-readable result: `docs/verification_results.json`
- Landing screenshot: `docs/screenshots/landing.png`
- Login screenshot: `docs/screenshots/login.png`
- Public dataset preview screenshot: `docs/screenshots/public-dataset-preview.png`
- Public dataset analysis workspace screenshot: `docs/screenshots/public-dataset-analysis-workspace.png`
- Public dataset PDF report screenshot: `docs/screenshots/public-dataset-pdf-report.png`

The current README screenshots are rendered from the running Next.js production server or from generated backend PDF output. The public dataset screenshots use the MoveNet artifacts documented in `docs/DATASET.md`; no screenshot was manually painted or fabricated.

## Triangulation verification

A known-camera test projects a known 3D point into two calibrated views, reconstructs it with linear triangulation, and verifies both reconstruction error and mean reprojection error below `1e-6`.

## Production model status

Implemented and type-checked:

- `MoveNetONNXPoseEstimator`
- ONNX Runtime CPU preprocessing and postprocessing
- model hash and metadata persistence
- SHA-256-pinned downloader
- production configuration defaults to `movenet`

The MoveNet ONNX binary is exercised by the public dataset demo documented in `docs/DATASET.md`. The controlled fixture adapter remains available for deterministic CI verification and does not substitute for the normal production configuration.

## Docker status

The Compose stack, service Dockerfiles, health checks, non-root runtime users, PostgreSQL, Redis, MinIO, Celery, web, Prometheus, and Grafana configuration are included. Docker health could not be executed because the sandbox has no Docker executable.

## Known limitations

- Full chessboard and ChArUco capture UI is not implemented; calibration persistence, geometric triangulation, reprojection calculations, API records, and tests are implemented.
- Local protected artifact storage is the executed path. MinIO is included in Compose, but the full signed-URL MinIO adapter remains an extension point.
- Refresh-token rotation, MFA/SSO, legal holds, automatic retention deletion, full annotated MP4 generation, and learned multi-person tracking are not claimed complete.
- The interactive workspace supports source video, pose data, evidence, synchronized timeline cursor, and React Three Fiber playback. Current public dataset screenshots are captured from the running Next.js production server.
- Medical diagnosis and millimeter-accurate monocular measurement are explicitly out of scope.
