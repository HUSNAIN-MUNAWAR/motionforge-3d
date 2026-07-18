from __future__ import annotations
import argparse
import math
from pathlib import Path
import cv2
import numpy as np
from packages.pose_core.marker_estimator import MARKERS

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


def pose(t: float):
    # Controlled squat-like motion. Coordinates are generated as fixture geometry,
    # while the verification estimator must recover them from encoded pixels.
    phase = (1 - math.cos(2 * math.pi * t)) / 2
    hip_y = 250 + 80 * phase
    knee_y = 350 + 25 * phase
    return {
        "nose": (320, 95 + 15 * phase),
        "left_shoulder": (270, 155 + 25 * phase),
        "right_shoulder": (370, 155 + 25 * phase),
        "left_elbow": (235, 220 + 20 * phase),
        "right_elbow": (405, 220 + 20 * phase),
        "left_wrist": (215, 285 + 10 * phase),
        "right_wrist": (425, 285 + 10 * phase),
        "left_hip": (285, hip_y),
        "right_hip": (355, hip_y),
        "left_knee": (255 - 25 * phase, knee_y),
        "right_knee": (385 + 25 * phase, knee_y),
        "left_ankle": (245, 445),
        "right_ankle": (395, 445),
    }


def generate(path: Path, duration: float = 4.0, fps: int = 24):
    path.parent.mkdir(parents=True, exist_ok=True)
    size = (640, 480)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore[attr-defined]
    writer = cv2.VideoWriter(str(path), fourcc, fps, size)
    if not writer.isOpened():
        raise RuntimeError("MP4 encoder unavailable")
    for i in range(int(duration * fps)):
        frame = np.zeros((size[1], size[0], 3), np.uint8)
        frame[:] = (8, 13, 22)
        p = pose((i / fps) % 2 / 2)
        for a, b in EDGES:
            cv2.line(
                frame, tuple(map(int, p[a])), tuple(map(int, p[b])), (70, 85, 105), 5, cv2.LINE_AA
            )
        for name, xy in p.items():
            cv2.circle(frame, tuple(map(int, xy)), 8, MARKERS[name], -1, cv2.LINE_AA)
        cv2.putText(
            frame,
            "CONTROLLED MOTION FIXTURE",
            (18, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (230, 245, 255),
            2,
        )
        cv2.putText(
            frame, f"t={i / fps:.2f}s", (18, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (130, 180, 210), 1
        )
        writer.write(frame)
    writer.release()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("output", nargs="?", default="tests/fixtures/controlled_squat.mp4")
    a = p.parse_args()
    generate(Path(a.output))
    print(a.output)
