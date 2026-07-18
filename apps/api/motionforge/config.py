from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MOTIONFORGE_", extra="ignore")
    app_name: str = "MotionForge 3D"
    environment: str = "development"
    secret_key: str = "development-only-change-me"
    database_url: str = "sqlite:///./motionforge.db"
    storage_root: Path = Path("storage")
    access_token_minutes: int = 30
    max_upload_mb: int = 250
    max_video_seconds: int = 600
    model_backend: str = "movenet"
    model_path: Path = Path("models/movenet-singlepose-lightning.onnx")
    sample_fps: float = 8.0
    queue_mode: str = "database"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    allowed_origins: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
