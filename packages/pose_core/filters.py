from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np


class ExponentialSmoother:
    def __init__(self, alpha: float = 0.35) -> None:
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in (0,1]")
        self.alpha = alpha
        self.value: np.ndarray | None = None

    def update(self, x: np.ndarray) -> np.ndarray:
        self.value = (
            x.astype(float)
            if self.value is None
            else self.alpha * x + (1 - self.alpha) * self.value
        )
        return self.value.copy()


@dataclass
class LowPass:
    alpha: float
    value: float | None = None

    def apply(self, value: float, alpha: float | None = None) -> float:
        a = self.alpha if alpha is None else alpha
        self.value = value if self.value is None else a * value + (1 - a) * self.value
        return self.value


class OneEuroFilter:
    def __init__(
        self,
        frequency: float = 30.0,
        min_cutoff: float = 1.0,
        beta: float = 0.02,
        d_cutoff: float = 1.0,
    ) -> None:
        self.frequency = frequency
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x = LowPass(self._alpha(min_cutoff))
        self.dx = LowPass(self._alpha(d_cutoff))
        self.last_t: float | None = None

    def _alpha(self, cutoff: float) -> float:
        te = 1.0 / self.frequency
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / te)

    def __call__(self, value: float, timestamp: float) -> float:
        if self.last_t is not None and timestamp > self.last_t:
            self.frequency = 1.0 / (timestamp - self.last_t)
        self.last_t = timestamp
        prev = self.x.value if self.x.value is not None else value
        derivative = (value - prev) * self.frequency
        edx = self.dx.apply(derivative, self._alpha(self.d_cutoff))
        cutoff = self.min_cutoff + self.beta * abs(edx)
        return self.x.apply(value, self._alpha(cutoff))
