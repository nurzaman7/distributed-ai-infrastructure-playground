from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class AttentionOutput:
    tokens: list[str]
    attention_matrix: list[list[float]]
    entropy_per_token: list[float]


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x, axis=-1, keepdims=True)
    ex = np.exp(x)
    return ex / np.sum(ex, axis=-1, keepdims=True)


def simulate_attention(tokens: list[str], seed: int = 42) -> AttentionOutput:
    n = max(1, len(tokens))
    rng = np.random.default_rng(seed)

    q = rng.normal(0, 1, (n, 32))
    k = rng.normal(0, 1, (n, 32))

    logits = (q @ k.T) / math.sqrt(32)
    attn = _softmax(logits)

    entropy = -np.sum(attn * np.log(attn + 1e-9), axis=1)

    return AttentionOutput(
        tokens=tokens,
        attention_matrix=attn.round(6).tolist(),
        entropy_per_token=entropy.round(6).tolist(),
    )
