from __future__ import annotations
import hashlib
from pathlib import Path
from uuid import uuid4
import cv2
from fastapi import UploadFile
from ..config import get_settings

ALLOWED = {"video/mp4", "video/quicktime", "video/webm", "application/octet-stream"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_upload(file: UploadFile, organization_id: str, session_id: str) -> tuple[Path, dict]:
    s = get_settings()
    suffix = Path(file.filename or "video.mp4").suffix.lower()
    if suffix not in {".mp4", ".mov", ".webm"}:
        raise ValueError("Only MP4, MOV, and WebM files are accepted")
    if file.content_type not in ALLOWED:
        raise ValueError("Unsupported MIME type")
    target = s.storage_root / "uploads" / organization_id / session_id / f"{uuid4().hex}{suffix}"
    target.parent.mkdir(parents=True, exist_ok=True)
    size = 0
    with target.open("wb") as out:
        while chunk := file.file.read(1024 * 1024):
            size += len(chunk)
            if size > s.max_upload_mb * 1024 * 1024:
                target.unlink(missing_ok=True)
                raise ValueError("File exceeds configured upload limit")
            out.write(chunk)
    cap = cv2.VideoCapture(str(target))
    if not cap.isOpened():
        target.unlink(missing_ok=True)
        raise ValueError("Video decoding validation failed")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    duration = frames / fps if fps else 0
    ok, first = cap.read()
    cap.release()
    if not ok or first is None:
        target.unlink(missing_ok=True)
        raise ValueError("Video contains no decodable frames")
    if duration > s.max_video_seconds:
        target.unlink(missing_ok=True)
        raise ValueError("Video exceeds configured duration")
    codec = "".join(chr((fourcc >> 8 * i) & 0xFF) for i in range(4)).strip("\x00")
    return target, {
        "size_bytes": size,
        "sha256": sha256_file(target),
        "duration_s": duration,
        "fps": fps,
        "width": width,
        "height": height,
        "codec": codec,
    }
