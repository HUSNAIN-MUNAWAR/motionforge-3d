FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app:/app/apps/api
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libgl1 libglib2.0-0 curl && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 10001 motionforge
WORKDIR /app
COPY pyproject.toml ./
COPY apps ./apps
COPY packages ./packages
COPY configs ./configs
COPY alembic ./alembic
COPY alembic.ini ./
RUN pip install --no-cache-dir ".[postgres,queue,storage]"
USER motionforge
EXPOSE 8000
CMD ["uvicorn","motionforge.main:app","--host","0.0.0.0","--port","8000"]
