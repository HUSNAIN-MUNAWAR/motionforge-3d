from __future__ import annotations
from dataclasses import dataclass
import math
from .types import PoseFrameResult


@dataclass
class TrackState:
    track_id: int
    center: tuple[float, float]
    last_frame: int


class CentroidTracker:
    def __init__(self, max_distance: float = 0.2, expiry_frames: int = 15) -> None:
        self.max_distance = max_distance
        self.expiry_frames = expiry_frames
        self.next_id = 1
        self.tracks: dict[int, TrackState] = {}

    def assign(self, detections: list[PoseFrameResult], frame_index: int) -> list[PoseFrameResult]:
        self.tracks = {
            k: v for k, v in self.tracks.items() if frame_index - v.last_frame <= self.expiry_frames
        }
        available = set(self.tracks)
        for d in detections:
            if d.bbox:
                c = ((d.bbox[0] + d.bbox[2]) / 2, (d.bbox[1] + d.bbox[3]) / 2)
            else:
                xs = [p.x for p in d.landmarks.values()]
                ys = [p.y for p in d.landmarks.values()]
                c = (sum(xs) / len(xs), sum(ys) / len(ys))
            best = None
            best_dist = float("inf")
            for tid in available:
                dist = math.dist(c, self.tracks[tid].center)
                if dist < best_dist:
                    best, best_dist = tid, dist
            if best is None or best_dist > self.max_distance:
                best = self.next_id
                self.next_id += 1
            else:
                available.remove(best)
            d.track_id = best
            self.tracks[best] = TrackState(best, c, frame_index)
        return detections
