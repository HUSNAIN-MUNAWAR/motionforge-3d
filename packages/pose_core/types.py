from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Literal

CoordinateSystem = Literal["image_normalized", "image_pixel", "camera_plane_3d", "world_3d"]


@dataclass(slots=True)
class PoseLandmark:
    name: str
    x: float
    y: float
    z: float = 0.0
    confidence: float = 0.0
    visibility: float = 0.0
    interpolated: bool = False


@dataclass(slots=True)
class PoseFrameResult:
    frame_index: int
    timestamp_s: float
    track_id: int
    landmarks: dict[str, PoseLandmark]
    bbox: tuple[float, float, float, float] | None = None
    score: float = 0.0
    coordinate_system: CoordinateSystem = "image_normalized"
    source: Literal["raw", "filtered"] = "raw"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["landmarks"] = {k: asdict(v) for k, v in self.landmarks.items()}
        return data


@dataclass(slots=True)
class PoseModelMetadata:
    name: str
    version: str
    runtime: str
    input_size: tuple[int, int]
    model_hash: str | None = None
    mode: str = "single_person"
    notes: str = ""


@dataclass(slots=True)
class PoseSequence:
    schema_version: str
    session_id: str
    track_id: int
    coordinate_system: CoordinateSystem
    unit: str
    frames: list[PoseFrameResult] = field(default_factory=list)
    model: PoseModelMetadata | None = None
    calibration: dict | None = None

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "track_id": self.track_id,
            "coordinate_system": self.coordinate_system,
            "unit": self.unit,
            "model": asdict(self.model) if self.model else None,
            "calibration": self.calibration,
            "frames": [f.to_dict() for f in self.frames],
        }
