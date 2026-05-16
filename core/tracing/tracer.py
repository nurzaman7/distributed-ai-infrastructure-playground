from __future__ import annotations

from uuid import uuid4
from core.tracing.context import current_span_id, current_trace_id


class Tracer:
    def start_trace(self) -> tuple[str, str]:
        trace_id = uuid4().hex
        span_id = uuid4().hex[:16]
        current_trace_id.set(trace_id)
        current_span_id.set(span_id)
        return trace_id, span_id


tracer = Tracer()
