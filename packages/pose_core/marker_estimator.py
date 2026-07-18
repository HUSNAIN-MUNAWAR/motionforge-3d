from __future__ import annotations
import cv2
import numpy as np
from .base import PoseEstimator
from .types import PoseFrameResult, PoseLandmark, PoseModelMetadata

# Verification/calibration adapter: actual image segmentation over color-coded fiducials.
# It is intentionally not the production default and is never presented as a general human model.
MARKERS = {
    "nose": (0, 255, 255),
    "left_shoulder": (255, 0, 0),
    "right_shoulder": (0, 0, 255),
    "left_elbow": (255, 128, 0),
    "right_elbow": (0, 128, 255),
    "left_wrist": (255, 0, 255),
    "right_wrist": (0, 255, 0),
    "left_hip": (255, 255, 0),
    "right_hip": (128, 0, 255),
    "left_knee": (255, 255, 255),
    "right_knee": (0, 128, 128),
    "left_ankle": (128, 255, 0),
    "right_ankle": (128, 128, 0),
}


class ColorMarkerPoseEstimator(PoseEstimator):
    def __init__(self, tolerance: int = 20) -> None:
        self.tolerance = tolerance

    @property
    def metadata(self) -> PoseModelMetadata:
        return PoseModelMetadata(
            name="opencv-color-fiducial-pose",
            version="1.0.0",
            runtime=f"OpenCV {cv2.__version__}",
            input_size=(0, 0),
            mode="single_person",
            notes="Controlled verification/calibration adapter; not a general human pose model.",
        )

    def estimate(
        self, frame_bgr: np.ndarray, frame_index: int, timestamp_s: float
    ) -> list[PoseFrameResult]:
        h, w = frame_bgr.shape[:2]
        landmarks: dict[str, PoseLandmark] = {}
        for name, bgr in MARKERS.items():
            target = np.array(bgr, dtype=np.int16)
            diff = np.abs(frame_bgr.astype(np.int16) - target)
            mask = np.all(diff <= self.tolerance, axis=2).astype(np.uint8) * 255
            n, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
            if n <= 1:
                continue
            i = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
            area = int(stats[i, cv2.CC_STAT_AREA])
            if area < 10:
                continue
            x, y = centroids[i]
            conf = min(1.0, area / 80.0)
            landmarks[name] = PoseLandmark(
                name=name, x=float(x / w), y=float(y / h), confidence=conf, visibility=conf
            )
        if len(landmarks) < 6:
            return []
        xs = [p.x for p in landmarks.values()]
        ys = [p.y for p in landmarks.values()]
        result = PoseFrameResult(
            frame_index=frame_index,
            timestamp_s=timestamp_s,
            track_id=1,
            landmarks=landmarks,
            bbox=(min(xs), min(ys), max(xs), max(ys)),
            score=float(np.mean([p.confidence for p in landmarks.values()])),
        )
        return [result]
