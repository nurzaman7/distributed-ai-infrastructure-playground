from __future__ import annotations

import random
from time import perf_counter, sleep

from core.tracing.models import TraceRecord
from core.tracing.tracer import tracer


def run_inference(prompt: str) -> TraceRecord:
    trace_id, span_id = tracer.start_trace()
    started = perf_counter()

    # Simulate variable runtime and occasional failures
    base_sleep = random.uniform(0.01, 0.12)
    if random.random() < 0.03:
        base_sleep += random.uniform(0.2, 0.8)
    sleep(base_sleep)

    status = "success"
    err = None
    output = f"simulated response for: {prompt[:64]}"
    if random.random() < 0.02:
        status = "error"
        err = "simulated_timeout"
        output = ""

    latency_ms = (perf_counter() - started) * 1000
    tokens_in = len(prompt.split())
    tokens_out = len(output.split())
    memory_mb = random.uniform(200, 900)

    return TraceRecord(
        trace_id=trace_id,
        span_id=span_id,
        input=prompt,
        output=output,
        latency_ms=round(latency_ms, 3),
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        memory_mb=round(memory_mb, 3),
        status=status,
        error=err,
        metadata={"runtime": "simulated", "batch_size": 1},
    )
