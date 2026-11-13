"""Wilson interval and the paired bootstrap."""

from __future__ import annotations

import math

import numpy as np

Z95 = 1.959963984540054


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """95% Wilson score interval for k successes in n trials (0, 0 for n = 0)."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centre - half), min(1.0, centre + half)


def f1(tp: float, fp: float, fn: float) -> float:
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


def resample_counts(n: int, resamples: int, seed: int) -> np.ndarray:
    """How often each of n records is drawn in each resample, shape (resamples, n). Same seed, same draws, so
    every parser is resampled alike (a paired bootstrap)."""
    rng = np.random.default_rng(seed)
    return rng.multinomial(n, np.full(n, 1.0 / n), size=resamples).astype(np.float32)


def percentile_interval(values: np.ndarray) -> tuple[float, float]:
    lo, hi = np.percentile(values, [2.5, 97.5])
    return float(lo), float(hi)
