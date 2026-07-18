from __future__ import annotations
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
os.environ["MOTIONFORGE_DATABASE_URL"] = "sqlite:///./verification.db"
os.environ["MOTIONFORGE_STORAGE_ROOT"] = "verification_storage"
os.environ["MOTIONFORGE_MODEL_BACKEND"] = "marker"
sys.path[:0] = [str(ROOT), str(ROOT / "apps/api")]
from scripts.demo.generate_marker_video import generate
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


def main():
    Path("verification.db").unlink(missing_ok=True)
    shutil.rmtree("verification_storage", ignore_errors=True)
    Base.metadata.create_all(engine)
    video = Path("tests/fixtures/controlled_squat.mp4")
    generate(video)
    import cv2

    cap = cv2.VideoCapture(str(video))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    started = time.perf_counter()
    with SessionLocal() as db:
        user = User(
            email="demo@motionforge.local",
            display_name="Demo Analyst",
            password_hash=hash_password("MotionForgeDemo!2026"),
        )
        org = Organization(name="MotionForge Lab", slug="motionforge-lab")
        db.add_all([user, org])
        db.flush()
        db.add(Membership(organization_id=org.id, user_id=user.id, role="owner"))
        subject = Subject(
            organization_id=org.id,
            display_name="ATH-001",
            external_reference="ATH-001",
            consent_status="recorded",
            created_by=user.id,
            tags=["controlled-fixture"],
        )
        db.add(subject)
        db.flush()
        session = Session(
            organization_id=org.id,
            subject_id=subject.id,
            title="Controlled Squat Verification",
            movement_template="squat",
            created_by=user.id,
            processing_configuration={"sample_fps": 8},
        )
        db.add(session)
        db.flush()
        media = MediaAsset(
            organization_id=org.id,
            session_id=session.id,
            storage_key=str(video),
            original_filename=video.name,
            mime_type="video/mp4",
            sha256=sha256_file(video),
            size_bytes=video.stat().st_size,
            duration_s=count / fps,
            width=w,
            height=h,
            fps=fps,
            codec="mp4v",
            metadata_json={"fixture": "controlled"},
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
        result = run_job(db, job.id)
        report = generate_report(db, session, user.id)
        elapsed = time.perf_counter() - started
        output = {
            "environment": {
                "os": platform.platform(),
                "python": sys.version.split()[0],
                "node": subprocess.run(
                    ["node", "--version"], capture_output=True, text=True
                ).stdout.strip(),
                "docker": "unavailable in sandbox",
            },
            "workflow": {
                "session_id": session.id,
                "job_id": job.id,
                "job_state": job.state,
                "decoded_frames": result.quality_metrics["decoded_frames"],
                "analyzed_frames": result.quality_metrics["analyzed_frames"],
                "valid_pose_frames": result.quality_metrics["valid_pose_frames"],
                "average_landmark_confidence": result.quality_metrics[
                    "average_landmark_confidence"
                ],
                "pose_model": result.model_metadata["name"],
                "processing_duration_s": round(elapsed, 3),
                "repetitions": len(result.analytics["repetitions"]),
                "events": len(result.analytics["events"]),
                "score": result.analytics["score"]["final"],
                "pose_artifact": result.pose_artifact_key,
                "evidence_artifact": result.evidence_key,
                "report_artifact": report.storage_key,
            },
        }
        Path("docs/verification_results.json").write_text(json.dumps(output, indent=2))
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
