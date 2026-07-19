from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any, cast
import cv2
import numpy as np
from .base import PoseEstimator
from .types import PoseFrameResult, PoseLandmark, PoseModelMetadata

NAMES = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
]


class MoveNetONNXPoseEstimator(PoseEstimator):
    """Production CPU adapter for MoveNet SinglePose Lightning ONNX.

    The repository intentionally does not redistribute the model. Run scripts/models/download_movenet.py
    on a networked machine and set MOTIONFORGE_MODEL_PATH.
    """

    def __init__(self, model_path: str | Path, confidence_threshold: float = 0.2) -> None:
        self.path = Path(model_path)
        if not self.path.exists():
            raise FileNotFoundError(f"MoveNet model not found: {self.path}")
        self.session: Any | None = None
        self.net: Any | None = None
        self.input_name = ""
        self.input_type = ""
        try:
            import onnxruntime as ort

            self.session = ort.InferenceSession(str(self.path), providers=["CPUExecutionProvider"])
            model_input = self.session.get_inputs()[0]
            self.input_name = model_input.name
            self.input_type = model_input.type
            self.runtime = f"ONNX Runtime {ort.__version__}"
        except Exception:
            self.net = cv2.dnn.readNetFromONNX(str(self.path))
            self.runtime = f"OpenCV DNN {cv2.__version__}"
        self.threshold = confidence_threshold
        self._hash = hashlib.sha256(self.path.read_bytes()).hexdigest()

    @property
    def metadata(self) -> PoseModelMetadata:
        return PoseModelMetadata(
            name="MoveNet SinglePose Lightning",
            version="onnx-main",
            runtime=self.runtime,
            input_size=(192, 192),
            model_hash=self._hash,
            mode="single_person",
            notes="Apache-2.0 model; camera-relative 2D landmarks. Monocular depth is not metric.",
        )

    def estimate(
        self, frame_bgr: np.ndarray, frame_index: int, timestamp_s: float
    ) -> list[PoseFrameResult]:
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (192, 192), interpolation=cv2.INTER_LINEAR)
        if self.session is not None:
            dtype = np.int32 if "int32" in self.input_type else np.float32
            blob = resized.astype(dtype)[None, ...]
            out = np.asarray(self.session.run(None, {self.input_name: blob})[0]).reshape(-1, 3)
        else:
            blob = resized.astype(np.float32)[None, ...]
            # Accommodate NHWC or NCHW exports.
            input_shape = None
            if self.net is not None and hasattr(self.net, "getInputDetails"):
                details = cast(Any, self.net).getInputDetails()
                if details:
                    input_shape = getattr(details[0], "shape", None)
            if input_shape and len(input_shape) == 4 and input_shape[1] == 3:
                blob = np.transpose(blob, (0, 3, 1, 2))
            self.net.setInput(blob)
            out = np.asarray(self.net.forward()).reshape(-1, 3)
        if out.shape[0] < 17:
            return []
        landmarks: dict[str, PoseLandmark] = {}
        for name, (y, x, score) in zip(NAMES, out[:17]):
            score = float(score)
            if score >= self.threshold:
                landmarks[name] = PoseLandmark(
                    name=name, x=float(x), y=float(y), confidence=score, visibility=score
                )
        if len(landmarks) < 6:
            return []
        xs = [p.x for p in landmarks.values()]
        ys = [p.y for p in landmarks.values()]
        return [
            PoseFrameResult(
                frame_index=frame_index,
                timestamp_s=timestamp_s,
                track_id=1,
                landmarks=landmarks,
                bbox=(min(xs), min(ys), max(xs), max(ys)),
                score=float(np.mean([p.confidence for p in landmarks.values()])),
            )
        ]
