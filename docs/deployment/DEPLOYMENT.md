# Deployment Guide

1. Provision PostgreSQL 16, Redis 7, and private S3-compatible storage.
2. Generate a 32+ byte application secret and separate infrastructure credentials.
3. Download and hash-verify the MoveNet ONNX model using `scripts/models/download_movenet.py`.
4. Build API, worker, and web images from the included Dockerfiles.
5. Run `alembic upgrade head` before API traffic.
6. Use one CPU worker initially and increase only after observing memory and latency.
7. Put TLS and request-size controls at ingress.
8. Keep source media and artifacts private; never authorize from a raw object key alone.
9. Enable monitoring profile or send structured logs/metrics to the platform stack.
10. Back up PostgreSQL and object storage consistently and test restore procedures.

The Compose file is for local evaluation, not a substitute for production secret management, backups, or network policy.
