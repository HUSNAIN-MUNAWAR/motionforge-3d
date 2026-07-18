from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.signal import find_peaks


@dataclass(slots=True)
class Repetition:
    index: int
    start_s: float
    peak_s: float
    end_s: float
    duration_s: float
    amplitude: float
    confidence: float


def detect_repetitions(
    values, timestamps, prominence=15.0, min_duration=0.45, max_duration=8.0, invert=False
):
    y = np.asarray(values, float)
    t = np.asarray(timestamps, float)
    if len(y) < 5:
        return []
    signal = -y if invert else y
    distance = max(1, int(len(y) * min_duration / max(t[-1] - t[0], 1e-6)))
    peaks, props = find_peaks(signal, prominence=prominence, distance=distance)
    valleys, _ = find_peaks(-signal, distance=max(1, distance // 2))
    valley_list = valleys.tolist()
    if len(signal) > 1 and signal[0] <= signal[1]:
        valley_list.insert(0, 0)
    if len(signal) > 1 and signal[-1] <= signal[-2]:
        valley_list.append(len(signal) - 1)
    valleys = np.asarray(sorted(set(valley_list)), dtype=int)
    reps = []
    for peak in peaks:
        before = valleys[valleys < peak]
        after = valleys[valleys > peak]
        if not len(before) or not len(after):
            continue
        start = int(before[-1])
        end = int(after[0])
        dur = float(t[end] - t[start])
        if not min_duration <= dur <= max_duration:
            continue
        amp = float(signal[peak] - max(signal[start], signal[end]))
        conf = float(min(1.0, max(0.0, amp / (prominence * 2))))
        reps.append(
            Repetition(
                len(reps) + 1, float(t[start]), float(t[peak]), float(t[end]), dur, amp, conf
            )
        )
    return reps
