from __future__ import annotations

import numpy as np


def synthetic_activations(num_layers: int = 6, hidden_dim: int = 64, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    layers: dict[str, dict] = {}
    for i in range(num_layers):
        vec = rng.normal(0, 1, hidden_dim)
        layers[f"layer_{i}"] = {
            "mean": float(np.mean(vec)),
            "std": float(np.std(vec)),
            "max": float(np.max(vec)),
            "min": float(np.min(vec)),
            "l2_norm": float(np.linalg.norm(vec)),
            "vector": vec.round(6).tolist(),
        }
    return layers
