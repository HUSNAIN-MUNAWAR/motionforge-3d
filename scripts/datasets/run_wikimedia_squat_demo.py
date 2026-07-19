from __future__ import annotations

import gzip
import json
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2

from scripts.datasets.download_wikimedia_squat import DEFAULT_OUTPUT, main as download_dataset

ROOT = Path(__file__).resolve().parents[2]
DATASET_VIDEO = ROOT / DEFAULT_OUTPUT
DB_PATH = ROOT / "public_dataset_demo.db"
STORAGE_ROOT = ROOT / "public_dataset_demo_storage"
RESULT_PATH = ROOT / "docs/public_dataset_results.json"
ARTIFACT_DIR = ROOT / "docs/public_dataset_artifacts"
WEB_DEMO_DIR = ROOT / "apps/web/public/demo"


def configure_environment() -> None:
    os.environ["MOTIONFORGE_DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
    os.environ["MOTIONFORGE_STORAGE_ROOT"] = str(STORAGE_ROOT)
    os.environ["MOTIONFORGE_MODEL_BACKEND"] = "movenet"
    os.environ["MOTIONFORGE_MODEL_PATH"] = str(ROOT / "models/movenet-singlepose-lightning.onnx")


def read_video_metadata(path: Path) -> dict:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Video cannot be decoded: {path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap.release()
    return {
        "fps": fps,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration_s": frame_count / fps if fps else 0,
    }


def main() -> None:
    os.chdir(ROOT)
    if not DATASET_VIDEO.exists():
        download_dataset()
    configure_environment()
    model_path = Path(os.environ["MOTIONFORGE_MODEL_PATH"])
    if not model_path.exists():
        raise SystemExit(
            "MoveNet ONNX model is missing. Run: "
            "py scripts/models/download_movenet.py --output models/movenet-singlepose-lightning.onnx"
        )

    from motionforge.db import Base, SessionLocal, engine
    from motionforge.models import (
        MediaAsset,
        Membership,
        Organization,
        ProcessingJob,
        Session,
        Subject,
        User,
    )
    from motionforge.security import hash_password
    from motionforge.services.analysis import run_job
    from motionforge.services.reporting import generate_report
    from motionforge.services.storage import sha256_file

    DB_PATH.unlink(missing_ok=True)
    shutil.rmtree(STORAGE_ROOT, ignore_errors=True)
    Base.metadata.create_all(engine)
    meta = read_video_metadata(DATASET_VIDEO)
    started = time.perf_counter()

    with SessionLocal() as db:
        user = User(
            email="public-demo@motionforge.local",
            display_name="Public Dataset Analyst",
            password_hash=hash_password("MotionForgePublic!2026"),
        )
        org = Organization(
            name="MotionForge Public Dataset Lab",
            slug="motionforge-public-dataset-lab",
        )
        db.add_all([user, org])
        db.flush()
        db.add(Membership(organization_id=org.id, user_id=user.id, role="owner"))
        subject = Subject(
            organization_id=org.id,
            display_name="Wikimedia squat demonstration sample",
            external_reference="WIKIMEDIA-SQUAT-CCBY3",
            consent_status="public_dataset",
            created_by=user.id,
            tags=["public-dataset", "wikimedia-commons", "cc-by-3.0"],
        )
        db.add(subject)
        db.flush()
        session = Session(
            organization_id=org.id,
            subject_id=subject.id,
            title="Public Dataset Weighted Squat Analysis",
            movement_template="squat",
            created_by=user.id,
            processing_configuration={
                "sample_fps": 4,
                "source_dataset": "Wikimedia Commons CC BY 3.0 squat demonstration video",
            },
        )
        db.add(session)
        db.flush()
        media = MediaAsset(
            organization_id=org.id,
            session_id=session.id,
            storage_key=str(DATASET_VIDEO),
            original_filename=DATASET_VIDEO.name,
            mime_type="video/webm",
            sha256=sha256_file(DATASET_VIDEO),
            size_bytes=DATASET_VIDEO.stat().st_size,
            duration_s=meta["duration_s"],
            width=meta["width"],
            height=meta["height"],
            fps=meta["fps"],
            codec="VP9",
            metadata_json={
                "dataset": "Wikimedia Commons squat exercise demonstration video",
                "license": "CC BY 3.0",
                "author": "FitnessScape",
                "source": "https://commons.wikimedia.org/wiki/File:Squat_-_exercise_demonstration_video.webm",
            },
        )
        db.add(media)
        db.flush()
        job = ProcessingJob(
            organization_id=org.id,
            session_id=session.id,
            media_asset_id=media.id,
            state="queued",
            stage="queued",
        )
        db.add(job)
        db.commit()

        analysis = run_job(db, job.id)
        report = generate_report(db, session, user.id)
        elapsed = round(time.perf_counter() - started, 3)

        with gzip.open(analysis.pose_artifact_key, "rt", encoding="utf-8") as fh:
            pose = json.load(fh)

        analysis_json = {
            "coordinate_system": analysis.coordinate_system,
            "unit": analysis.unit,
            "model_metadata": analysis.model_metadata,
            "quality_metrics": analysis.quality_metrics,
            "analytics": analysis.analytics,
            "events": analysis.analytics.get("events", []),
            "dataset": media.metadata_json,
            "session": {
                "title": session.title,
                "subject": subject.display_name,
                "organization": org.name,
                "demo_label": "Public dataset demo; not a customer or clinical dataset.",
            },
        }
        result = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dataset": {
                "name": "Squat - exercise demonstration video",
                "publisher": "Wikimedia Commons",
                "author": "FitnessScape",
                "source": media.metadata_json["source"],
                "license": "Creative Commons Attribution 3.0 Unported",
                "sha256": media.sha256,
                "file": DEFAULT_OUTPUT.as_posix(),
                "size_bytes": media.size_bytes,
                "format": "WebM VP9",
                **meta,
            },
            "workflow": {
                "processing_duration_s": elapsed,
                "job_state": job.state,
                "pose_model": analysis.model_metadata["name"],
                "runtime": analysis.model_metadata["runtime"],
                "decoded_frames": analysis.quality_metrics["decoded_frames"],
                "analyzed_frames": analysis.quality_metrics["analyzed_frames"],
                "valid_pose_frames": analysis.quality_metrics["valid_pose_frames"],
                "average_landmark_confidence": analysis.quality_metrics[
                    "average_landmark_confidence"
                ],
                "repetitions": len(analysis.analytics["repetitions"]),
                "events": len(analysis.analytics["events"]),
                "score": analysis.analytics["score"]["final"],
            },
            "artifacts": {
                "pose_sequence": "docs/public_dataset_artifacts/pose_sequence.json.gz",
                "evidence": "docs/public_dataset_artifacts/evidence.jpg",
                "report": "docs/public_dataset_artifacts/public_dataset_report.pdf",
                "web_analysis": "apps/web/public/demo/analysis.json",
                "web_pose": "apps/web/public/demo/pose.json",
                "web_video": "apps/web/public/demo/video.webm",
            },
        }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DEMO_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(analysis.pose_artifact_key, ARTIFACT_DIR / "pose_sequence.json.gz")
    shutil.copy2(analysis.evidence_key, ARTIFACT_DIR / "evidence.jpg")
    shutil.copy2(report.storage_key, ARTIFACT_DIR / "public_dataset_report.pdf")
    shutil.copy2(analysis.evidence_key, WEB_DEMO_DIR / "evidence.jpg")
    shutil.copy2(DATASET_VIDEO, WEB_DEMO_DIR / "video.webm")
    (WEB_DEMO_DIR / "analysis.json").write_text(json.dumps(analysis_json, indent=2))
    (WEB_DEMO_DIR / "pose.json").write_text(json.dumps(pose, indent=2))
    RESULT_PATH.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
