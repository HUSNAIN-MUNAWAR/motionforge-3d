FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app:/app/apps/api
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 10001 motionforge
WORKDIR /app
COPY pyproject.toml ./
COPY apps ./apps
COPY packages ./packages
COPY configs ./configs
RUN pip install --no-cache-dir ".[postgres,queue,storage]"
USER motionforge
CMD ["celery","-A","apps.worker.celery_app:celery_app","worker","--loglevel=INFO","--concurrency=1"]
