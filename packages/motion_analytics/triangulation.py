from __future__ import annotations
import cv2
import numpy as np


def projection_matrix(K, R, t):
    return np.asarray(K, float) @ np.hstack(
        [np.asarray(R, float), np.asarray(t, float).reshape(3, 1)]
    )


def triangulate_point(P1, P2, point1, point2):
    p1 = np.asarray(point1, float).reshape(2, 1)
    p2 = np.asarray(point2, float).reshape(2, 1)
    h = cv2.triangulatePoints(np.asarray(P1, float), np.asarray(P2, float), p1, p2).reshape(4)
    if abs(h[3]) < 1e-12:
        raise ValueError("degenerate triangulation")
    return h[:3] / h[3]


def project(P, point3d):
    h = np.append(np.asarray(point3d, float), 1.0)
    q = np.asarray(P, float) @ h
    return q[:2] / q[2]


def reprojection_error(P1, P2, point3d, point1, point2):
    return float(
        (
            np.linalg.norm(project(P1, point3d) - point1)
            + np.linalg.norm(project(P2, point3d) - point2)
        )
        / 2
    )
