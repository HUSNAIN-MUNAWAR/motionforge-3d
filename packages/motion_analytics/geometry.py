from __future__ import annotations
import numpy as np


def angle_degrees(a, b, c) -> float | None:
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    c = np.asarray(c, float)
    u = a - b
    v = c - b
    nu = np.linalg.norm(u)
    nv = np.linalg.norm(v)
    if nu < 1e-9 or nv < 1e-9:
        return None
    cos = float(np.clip(np.dot(u, v) / (nu * nv), -1, 1))
    return float(np.degrees(np.arccos(cos)))


def derivative(values, timestamps):
    v = np.asarray(values, float)
    t = np.asarray(timestamps, float)
    if len(v) < 2:
        return np.zeros_like(v)
    if np.any(np.diff(t) <= 0):
        raise ValueError("timestamps must be strictly increasing")
    return np.gradient(v, t)


def range_summary(values):
    v = np.asarray([x for x in values if x is not None], float)
    if not len(v):
        return {
            "min": None,
            "max": None,
            "range": None,
            "mean": None,
            "median": None,
            "std": None,
            "p05": None,
            "p95": None,
        }
    return {
        "min": float(v.min()),
        "max": float(v.max()),
        "range": float(v.max() - v.min()),
        "mean": float(v.mean()),
        "median": float(np.median(v)),
        "std": float(v.std()),
        "p05": float(np.percentile(v, 5)),
        "p95": float(np.percentile(v, 95)),
    }


def symmetry_percent(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    denom = max(abs(left), abs(right), 1e-9)
    return max(0.0, 100.0 * (1.0 - abs(left - right) / denom))
