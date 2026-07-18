import numpy as np
from packages.motion_analytics.geometry import angle_degrees, derivative, symmetry_percent


def test_right_angle():
    assert angle_degrees((1, 0), (0, 0), (0, 1)) == 90.0


def test_degenerate():
    assert angle_degrees((0, 0), (0, 0), (1, 0)) is None


def test_derivative_uses_timestamps():
    assert np.allclose(derivative([0, 2, 6], [0, 1, 2]), [2, 3, 4])


def test_symmetry_formula():
    assert symmetry_percent(90, 81) == 90.0
