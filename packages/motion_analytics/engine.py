from __future__ import annotations
from dataclasses import asdict
import numpy as np
from packages.pose_core.types import PoseFrameResult
from .geometry import angle_degrees, derivative, range_summary, symmetry_percent
from .repetition import detect_repetitions
from .rules import evaluate_threshold

JOINTS = {
    "left_elbow": ("left_shoulder", "left_elbow", "left_wrist"),
    "right_elbow": ("right_shoulder", "right_elbow", "right_wrist"),
    "left_shoulder": ("left_elbow", "left_shoulder", "left_hip"),
    "right_shoulder": ("right_elbow", "right_shoulder", "right_hip"),
    "left_hip": ("left_shoulder", "left_hip", "left_knee"),
    "right_hip": ("right_shoulder", "right_hip", "right_knee"),
    "left_knee": ("left_hip", "left_knee", "left_ankle"),
    "right_knee": ("right_hip", "right_knee", "right_ankle"),
}


def _point(frame, name):
    p = frame.landmarks.get(name)
    return None if p is None else (p.x, p.y, p.z)


def analyze(frames: list[PoseFrameResult], template: dict) -> dict:
    timestamps = [f.timestamp_s for f in frames]
    series: dict[str, list[float | None]] = {}
    for joint, (a, b, c) in JOINTS.items():
        vals = []
        for f in frames:
            pts = (_point(f, a), _point(f, b), _point(f, c))
            vals.append(angle_degrees(*pts) if all(x is not None for x in pts) else None)
        series[joint] = vals
    primary = template["primary_signal"]
    valid = [(t, v) for t, v in zip(timestamps, series[primary]) if v is not None]
    vt = [x[0] for x in valid]
    vv = [x[1] for x in valid]
    reps = detect_repetitions(
        vv,
        vt,
        prominence=template.get("prominence", 12),
        min_duration=template.get("min_duration", 0.45),
        max_duration=template.get("max_duration", 8),
        invert=template.get("invert", False),
    )
    summaries = {k: range_summary(v) for k, v in series.items()}
    velocities: dict[str, list[float]] = {}
    for k, vals in series.items():
        arr = np.array([np.nan if x is None else x for x in vals], float)
        if np.all(np.isnan(arr)):
            velocities[k] = []
            continue
        good = np.where(~np.isnan(arr))[0]
        arr = np.interp(np.arange(len(arr)), good, arr[good])
        velocities[k] = derivative(arr, timestamps).tolist()
    left = summaries.get("left_" + template["joint_family"], {}).get("range")
    right = summaries.get("right_" + template["joint_family"], {}).get("range")
    sym = symmetry_percent(left, right)
    events = []
    if template.get("max_trunk_inclination") is not None:
        # camera-plane trunk inclination relative to vertical
        trunk: list[float | None] = []
        for f in frames:
            ls = _point(f, "left_shoulder")
            rs = _point(f, "right_shoulder")
            lh = _point(f, "left_hip")
            rh = _point(f, "right_hip")
            if all(x is not None for x in (ls, rs, lh, rh)):
                s = np.mean([ls, rs], axis=0)
                h = np.mean([lh, rh], axis=0)
                vec = s - h
                trunk.append(float(np.degrees(np.arctan2(abs(vec[0]), abs(vec[1]) + 1e-9))))
            else:
                trunk.append(0.0)
        events = evaluate_threshold(
            "trunk_inclination", trunk, timestamps, template["max_trunk_inclination"]
        )
        series["trunk_inclination"] = trunk
    confidence = float(np.mean([p.confidence for f in frames for p in f.landmarks.values()]))
    components = {
        "range_completion": min(
            100.0,
            (summaries[primary]["range"] or 0) / max(template.get("target_range", 60), 1) * 100,
        ),
        "symmetry": sym if sym is not None else 0.0,
        "tempo_consistency": 100.0
        if len(reps) <= 1
        else max(0, 100 - np.std([r.duration_s for r in reps]) * 20),
        "tracking_confidence": confidence * 100,
        "repetition_completeness": min(100, len(reps) * 25),
    }
    weights = {
        "range_completion": 0.3,
        "symmetry": 0.2,
        "tempo_consistency": 0.15,
        "tracking_confidence": 0.2,
        "repetition_completeness": 0.15,
    }
    score = sum(components[k] * weights[k] for k in weights)
    return {
        "timestamps": timestamps,
        "series": series,
        "summaries": summaries,
        "velocities": velocities,
        "repetitions": [asdict(r) for r in reps],
        "events": [asdict(e) for e in events],
        "symmetry_percent": sym,
        "score": {
            "final": round(float(score), 2),
            "components": components,
            "weights": weights,
            "formula_version": "1.0",
        },
    }
