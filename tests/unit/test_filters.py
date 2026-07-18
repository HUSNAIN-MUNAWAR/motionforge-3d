import numpy as np
from packages.pose_core.filters import ExponentialSmoother, OneEuroFilter


def test_ema():
    f = ExponentialSmoother(0.5)
    assert np.allclose(f.update(np.array([0.0])), [0])
    assert np.allclose(f.update(np.array([2.0])), [1])


def test_one_euro_finite():
    f = OneEuroFilter()
    vals = [f(v, i / 30) for i, v in enumerate([0, 1, 0, 1])]
    assert all(np.isfinite(vals))
