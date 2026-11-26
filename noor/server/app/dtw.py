"""Dynamic Time Warping distance between two MFCC sequences."""

from __future__ import annotations

import numpy as np


def dtw_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Length-normalized DTW distance between feature sequences a and b.

    a, b are (n_frames, n_features). Lower means more similar articulation.
    """
    ta, tb = a.shape[0], b.shape[0]
    if ta == 0 or tb == 0:
        return float("inf")

    # Pairwise Euclidean distances between every frame of a and b.
    cost = np.sqrt(np.maximum(0.0, ((a[:, None, :] - b[None, :, :]) ** 2).sum(-1)))

    acc = np.full((ta + 1, tb + 1), np.inf)
    acc[0, 0] = 0.0
    for i in range(1, ta + 1):
        ci = cost[i - 1]
        row, prev = acc[i], acc[i - 1]
        for j in range(1, tb + 1):
            row[j] = ci[j - 1] + min(prev[j], row[j - 1], prev[j - 1])
    return float(acc[ta, tb] / (ta + tb))
