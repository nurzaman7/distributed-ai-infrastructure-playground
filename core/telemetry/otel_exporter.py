from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _to_unix_nanos(ts: str) -> int:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1_000_000_000)


def record_to_otel_span(record: dict[str, Any], service_name: str = "future-ai-systems") -> dict[str, Any]:
    start = _to_unix_nanos(record.get("timestamp", datetime.now(timezone.utc).isoformat()))
    latency_ms = float(record.get("latency_ms", 0.0) or 0.0)
    end = start + int(latency_ms * 1_000_000)

    attrs = {
        "service.name": service_name,
        "llm.provider": str(record.get("provider", "simulated")),
        "llm.model": str(record.get("model", "baseline-sim")),
        "llm.tokens.in": int(record.get("tokens_in", 0) or 0),
        "llm.tokens.out": int(record.get("tokens_out", 0) or 0),
        "llm.memory.mb": float(record.get("memory_mb", 0.0) or 0.0),
        "trace.status": str(record.get("status", "unknown")),
    }
    if record.get("error"):
        attrs["exception.message"] = str(record["error"])

    return {
        "trace_id": str(record.get("trace_id", "")),
        "span_id": str(record.get("span_id", "")),
        "name": "inference.request",
        "start_time_unix_nano": start,
        "end_time_unix_nano": end,
        "attributes": attrs,
    }


def export_otel_spans(records: list[dict[str, Any]], service_name: str = "future-ai-systems") -> list[dict[str, Any]]:
    return [record_to_otel_span(r, service_name=service_name) for r in records]
