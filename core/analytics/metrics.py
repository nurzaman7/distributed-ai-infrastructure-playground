from __future__ import annotations

import pandas as pd


def summarize(records: list[dict]) -> dict:
    df = pd.DataFrame(records)
    if df.empty:
        return {
            "count": 0,
            "latency": {"p50": 0.0, "p95": 0.0, "p99": 0.0},
            "error_rate": 0.0,
            "tokens": {"tokens_in": 0, "tokens_out": 0},
            "throughput_rps": 0.0,
        }

    latency_col = pd.to_numeric(df.get("latency_ms", 0), errors="coerce").fillna(0)
    p50 = float(latency_col.quantile(0.50))
    p95 = float(latency_col.quantile(0.95))
    p99 = float(latency_col.quantile(0.99))

    err_rate = float((df.get("status", "success") == "error").mean())
    tokens_in = int(pd.to_numeric(df.get("tokens_in", 0), errors="coerce").fillna(0).sum())
    tokens_out = int(pd.to_numeric(df.get("tokens_out", 0), errors="coerce").fillna(0).sum())

    # rough throughput using count / (sum latency seconds)
    denom = max(0.001, float(latency_col.sum() / 1000.0))
    rps = float(len(df) / denom)

    return {
        "count": int(len(df)),
        "latency": {"p50": p50, "p95": p95, "p99": p99},
        "error_rate": err_rate,
        "tokens": {"tokens_in": tokens_in, "tokens_out": tokens_out},
        "throughput_rps": round(rps, 3),
    }
