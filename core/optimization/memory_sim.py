from __future__ import annotations


def estimate_kv_memory_mb(tokens: int, hidden_size: int = 4096, bytes_per_value: int = 2) -> float:
    # rough formula: K and V for each token => 2 * hidden_size values
    total_bytes = tokens * 2 * hidden_size * bytes_per_value
    return round(total_bytes / (1024 * 1024), 3)
