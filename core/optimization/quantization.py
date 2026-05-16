from __future__ import annotations


def quantization_multiplier(mode: str) -> float:
    m = mode.lower()
    if m == "fp16":
        return 0.5
    if m == "int8":
        return 0.25
    if m == "int4":
        return 0.125
    return 1.0  # fp32 fallback


def effective_memory_mb(base_memory_mb: float, mode: str) -> float:
    return round(base_memory_mb * quantization_multiplier(mode), 3)
