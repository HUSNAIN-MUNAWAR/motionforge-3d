import numpy as np
from packages.motion_analytics.repetition import detect_repetitions


def test_repetitions():
    t = np.linspace(0, 6, 181)
    y = 90 + 45 * np.sin(2 * np.pi * t / 2)
    reps = detect_repetitions(y, t, prominence=20, min_duration=0.5, max_duration=3)
    assert 2 <= len(reps) <= 3
