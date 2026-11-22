from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/sample/wikimedia-squat/squat-exercise-demonstration.webm"
MODEL = ROOT / "models/movenet-singlepose-lightning.onnx"
OUTPUT_DIR = ROOT / "docs/runtime_evidence"
ANNOTATED = OUTPUT_DIR / "movenet-squat-runtime.mp4"
POSTER = OUTPUT_DIR / "movenet-squat-runtime-poster.jpg"
TRACE = OUTPUT_DIR / "movenet-squat-runtime-trace.csv"
POSE = OUTPUT_DIR / "movenet-squat-pose-sequence.json.gz"
SUMMARY = OUTPUT_DIR / "movenet-squat-runtime-summary.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def video_metadata(path: Path) -> dict[str, float | int]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not decode source video: {path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap.release()
    return {
        "fps": fps,
        "frames": frames,
        "width": width,
        "height": height,
        "duration_s": round(frames / fps, 6) if fps else 0.0,
    }


def artifact(path: Path) -> dict[str, str | int]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def main() -> None:
    os.chdir(ROOT)
    if not SOURCE.exists():
        raise SystemExit(
            "Source video is missing. Run: py scripts/datasets/download_wikimedia_squat.py"
        )
    if not MODEL.exists():
        raise SystemExit(
            "MoveNet model is missing. Run: "
            "py scripts/models/download_movenet.py --output models/movenet-singlepose-lightning.onnx"
        )

    sys.path[:0] = [str(ROOT), str(ROOT / "apps/api")]
    from packages.motion_analytics import analyze, load_template
    from packages.pose_core import MoveNetONNXPoseEstimator, process_video

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in (ANNOTATED, POSTER, TRACE, POSE, SUMMARY):
        path.unlink(missing_ok=True)

    estimator = MoveNetONNXPoseEstimator(MODEL)
    started = time.perf_counter()
    result = process_video(
        SOURCE,
        estimator,
        session_id="movenet-public-squat-runtime",
        artifact_dir=OUTPUT_DIR,
        sample_fps=4.0,
        annotated_output=ANNOTATED,
        trace_output=TRACE,
    )
    analytics = analyze(result["filtered"], load_template("squat"))
    elapsed = round(time.perf_counter() - started, 3)

    evidence = Path(result["evidence_path"])
    evidence.replace(POSTER)
    Path(result["pose_path"]).replace(POSE)

    cap = cv2.VideoCapture(str(ANNOTATED))
    encoded_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    encoded_fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    encoded_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    encoded_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap.release()

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "os": platform.platform(),
            "python": sys.version.split()[0],
            "opencv": cv2.__version__,
        },
        "source": {
            "dataset": "Wikimedia Commons squat exercise demonstration video",
            "publisher": "Wikimedia Commons",
            "author": "FitnessScape",
            "license": "Creative Commons Attribution 3.0 Unported",
            "url": "https://commons.wikimedia.org/wiki/File:Squat_-_exercise_demonstration_video.webm",
            "file": SOURCE.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(SOURCE),
            "metadata": video_metadata(SOURCE),
        },
        "model": {
            "name": estimator.metadata.name,
            "version": estimator.metadata.version,
            "runtime": estimator.metadata.runtime,
            "input_size": estimator.metadata.input_size,
            "model_sha256": estimator.metadata.model_hash,
            "backend": "ONNX Runtime CPUExecutionProvider",
            "path": MODEL.relative_to(ROOT).as_posix(),
        },
        "pipeline": {
            "sample_fps": 4.0,
            "decoded_frames": result["quality"]["decoded_frames"],
            "analyzed_frames": result["quality"]["analyzed_frames"],
            "valid_pose_frames": result["quality"]["valid_pose_frames"],
            "average_landmark_confidence": result["quality"]["average_landmark_confidence"],
            "processing_duration_s": elapsed,
            "processing_fps": round(result["quality"]["decoded_frames"] / elapsed, 3)
            if elapsed
            else 0.0,
            "repetitions": len(analytics["repetitions"]),
            "events": len(analytics["events"]),
            "score": analytics["score"]["final"],
            "encoded_output": {
                "frames": encoded_frames,
                "fps": encoded_fps,
                "width": encoded_width,
                "height": encoded_height,
            },
        },
        "artifacts": {
            "annotated_video": artifact(ANNOTATED),
            "poster": artifact(POSTER),
            "frame_trace": artifact(TRACE),
            "pose_sequence": artifact(POSE),
        },
        "claim_boundary": [
            "This is a real MoveNet SinglePose Lightning inference run over decoded Wikimedia video pixels.",
            "The overlay contains only landmarks emitted by the model at sampled frames; unsampled frames remain unannotated source pixels.",
            "The output is single-person, camera-relative 2D pose analytics, not metric 3D reconstruction or medical diagnosis.",
            "No manual detections, painted screenshots, fabricated metrics, or model training are used.",
        ],
    }
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
