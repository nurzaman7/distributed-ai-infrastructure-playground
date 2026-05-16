from __future__ import annotations

import numpy as np


def activation_drift_score(v1: list[float], v2: list[float]) -> float:
    a = np.array(v1, dtype=float)
    b = np.array(v2, dtype=float)
    if a.shape != b.shape:
        m = min(len(a), len(b))
        a = a[:m]
        b = b[:m]
    return float(np.linalg.norm(a - b))
