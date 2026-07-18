import numpy as np
from packages.motion_analytics.triangulation import (
    projection_matrix,
    project,
    reprojection_error,
    triangulate_point,
)


def test_triangulation_known_point():
    K = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], float)
    R = np.eye(3)
    P1 = projection_matrix(K, R, [0, 0, 0])
    P2 = projection_matrix(K, R, [-0.5, 0, 0])
    X = np.array([0.2, -0.1, 3.0])
    x1 = project(P1, X)
    x2 = project(P2, X)
    rec = triangulate_point(P1, P2, x1, x2)
    assert np.linalg.norm(rec - X) < 1e-6
    assert reprojection_error(P1, P2, rec, x1, x2) < 1e-6
