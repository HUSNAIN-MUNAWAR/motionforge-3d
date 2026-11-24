from __future__ import annotations
import csv
import gzip
import json
from pathlib import Path
import cv2
import numpy as np
from .base import PoseEstimator
from .filters import OneEuroFilter
from .tracking import CentroidTracker
from .types import PoseFrameResult, PoseLandmark, PoseSequence

EDGES = [
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
]


def smooth_sequence(frames: list[PoseFrameResult]) -> list[PoseFrameResult]:
    filters: dict[tuple[int, str, str], OneEuroFilter] = {}
    output = []
    for f in frames:
        landmarks = {}
        for name, p in f.landmarks.items():
            vals = []
            for axis, val in (("x", p.x), ("y", p.y), ("z", p.z)):
                key = (f.track_id, name, axis)
                filt = filters.setdefault(key, OneEuroFilter())
                vals.append(filt(val, f.timestamp_s))
            landmarks[name] = PoseLandmark(
                name=name,
                x=vals[0],
                y=vals[1],
                z=vals[2],
                confidence=p.confidence,
                visibility=p.visibility,
                interpolated=p.interpolated,
            )
        output.append(
            PoseFrameResult(
                f.frame_index,
                f.timestamp_s,
                f.track_id,
                landmarks,
                f.bbox,
                f.score,
                f.coordinate_system,
                "filtered",
            )
        )
    return output


def draw_overlay(frame: np.ndarray, pose: PoseFrameResult) -> np.ndarray:
    out = frame.copy()
    h, w = out.shape[:2]
    for a, b in EDGES:
        if a in pose.landmarks and b in pose.landmarks:
            pa = pose.landmarks[a]
            pb = pose.landmarks[b]
            cv2.line(
                out,
                (int(pa.x * w), int(pa.y * h)),
                (int(pb.x * w), int(pb.y * h)),
                (0, 220, 255),
                2,
                cv2.LINE_AA,
            )
    for p in pose.landmarks.values():
        cv2.circle(out, (int(p.x * w), int(p.y * h)), 4, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.putText(
        out,
        f"track {pose.track_id}  t={pose.timestamp_s:.2f}s",
        (12, 26),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 220, 255),
        2,
    )
    return out


def _write_evidence_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise RuntimeError(f"Could not write pose evidence image: {path}")


def process_video(
    video_path: str | Path,
    estimator: PoseEstimator,
    session_id: str,
    artifact_dir: str | Path,
    sample_fps: float = 8.0,
    max_frames: int | None = None,
    progress=None,
    annotated_output: str | Path | None = None,
    trace_output: str | Path | None = None,
) -> dict:
    video_path = Path(video_path)
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError("Video cannot be decoded")
    source_fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / source_fps if source_fps else 0
    stride = max(1, round(source_fps / sample_fps))
    tracker = CentroidTracker()
    raw = []
    trace_rows: list[dict[str, object]] = []
    analyzed = 0
    decoded = 0
    evidence_path = None
    annotated_path = Path(annotated_output) if annotated_output else None
    trace_path = Path(trace_output) if trace_output else None
    writer = None
    if annotated_path:
        annotated_path.parent.mkdir(parents=True, exist_ok=True)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        if width <= 0 or height <= 0:
            cap.release()
            raise RuntimeError(f"Video has invalid dimensions: {video_path}")
        output_fps = source_fps if source_fps > 0 else 30.0
        writer = cv2.VideoWriter(
            str(annotated_path),
            getattr(cv2, "VideoWriter_fourcc")(*"mp4v"),
            output_fps,
            (width, height),
        )
        if not writer.isOpened():
            cap.release()
            raise RuntimeError(f"Could not open annotated video writer: {annotated_path}")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        idx = decoded
        decoded += 1
        if idx % stride:
            if writer is not None:
                writer.write(frame)
            continue
        ts = idx / source_fps
        detections = tracker.assign(estimator.estimate(frame, idx, ts), idx)
        if detections:
            primary = max(detections, key=lambda d: d.score)
            raw.append(primary)
            analyzed += 1
            trace_rows.append(
                {
                    "frame_index": primary.frame_index,
                    "timestamp_s": round(primary.timestamp_s, 6),
                    "track_id": primary.track_id,
                    "score": round(primary.score, 6),
                    "landmark_count": len(primary.landmarks),
                    "bbox_x_min": round(primary.bbox[0], 6) if primary.bbox else "",
                    "bbox_y_min": round(primary.bbox[1], 6) if primary.bbox else "",
                    "bbox_x_max": round(primary.bbox[2], 6) if primary.bbox else "",
                    "bbox_y_max": round(primary.bbox[3], 6) if primary.bbox else "",
                }
            )
            if evidence_path is None:
                evidence_path = artifact_dir / "evidence.jpg"
                _write_evidence_image(evidence_path, draw_overlay(frame, primary))
            if writer is not None:
                writer.write(draw_overlay(frame, primary))
        elif writer is not None:
            writer.write(frame)
        if progress:
            progress(min(80, int(80 * decoded / max(1, frame_count))), "running_pose_estimation")
        if max_frames and analyzed >= max_frames:
            break
    cap.release()
    if writer is not None:
        writer.release()
    if trace_path:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "frame_index",
            "timestamp_s",
            "track_id",
            "score",
            "landmark_count",
            "bbox_x_min",
            "bbox_y_min",
            "bbox_x_max",
            "bbox_y_max",
        ]
        with trace_path.open("w", newline="", encoding="utf-8") as fh:
            writer_csv = csv.DictWriter(fh, fieldnames=fields)
            writer_csv.writeheader()
            writer_csv.writerows(trace_rows)
    if not raw:
        raise RuntimeError("No pose detected in sampled frames")
    filtered = smooth_sequence(raw)
    sequence = PoseSequence(
        "1.0",
        session_id,
        filtered[0].track_id,
        "camera_plane_3d",
        "normalized",
        filtered,
        estimator.metadata,
    )
    pose_path = artifact_dir / "pose_sequence.json.gz"
    with gzip.open(pose_path, "wt", encoding="utf-8") as fh:
        json.dump(sequence.to_dict(), fh, separators=(",", ":"))
    quality = {
        "decoded_frames": decoded,
        "analyzed_frames": analyzed,
        "valid_pose_frames": len(raw),
        "valid_frame_percentage": round(100 * len(raw) / max(1, analyzed), 2),
        "average_landmark_confidence": round(
            float(np.mean([p.confidence for f in raw for p in f.landmarks.values()])), 4
        ),
        "sample_fps": sample_fps,
        "source_fps": source_fps,
        "duration_s": duration,
    }
    return {
        "raw": raw,
        "filtered": filtered,
        "pose_path": str(pose_path),
        "evidence_path": str(evidence_path) if evidence_path else None,
        "annotated_path": str(annotated_path) if annotated_path else None,
        "trace_path": str(trace_path) if trace_path else None,
        "trace_rows": trace_rows,
        "quality": quality,
    }
