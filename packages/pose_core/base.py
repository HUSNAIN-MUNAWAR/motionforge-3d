from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
from .types import PoseFrameResult, PoseModelMetadata


class PoseEstimator(ABC):
    @property
    @abstractmethod
    def metadata(self) -> PoseModelMetadata: ...

    @abstractmethod
    def estimate(
        self, frame_bgr: np.ndarray, frame_index: int, timestamp_s: float
    ) -> list[PoseFrameResult]: ...
