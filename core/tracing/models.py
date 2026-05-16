from __future__ import annotations

from datetime import datetime, UTC
from pydantic import BaseModel, Field


class TraceRecord(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    input: str
    output: str
    latency_ms: float
    tokens_in: int = 0
    tokens_out: int = 0
    memory_mb: float = 0.0
    status: str = "success"
    error: str | None = None
    provider: str = "simulated"
    model: str = "baseline-sim"
    metadata: dict = Field(default_factory=dict)


class QueueMetrics(BaseModel):
    queue_depth: int = 0
    enqueued_total: int = 0
    dropped_total: int = 0
    written_total: int = 0
    flush_batches_total: int = 0
    errors_total: int = 0
