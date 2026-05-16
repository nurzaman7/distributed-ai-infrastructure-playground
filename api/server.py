from __future__ import annotations

from datetime import datetime, UTC
from threading import Event, Thread
from time import sleep

from fastapi import FastAPI
from pydantic import BaseModel, Field

from core.activations.drift import activation_drift_score
from core.activations.extractor import synthetic_activations
from core.analytics.metrics import summarize
from core.distributed import (
    DistributedWorkerPool,
    FailurePolicy,
    LeastQueueRouter,
    RequestQueue,
    RoundRobinRouter,
)
from core.distributed.fault_scenarios import get_scenario, scenario_names
from core.inference.kv_cache import KVCacheSimulator
from core.inference.simulator import run_inference
from core.optimization.memory_sim import estimate_kv_memory_mb
from core.optimization.quantization import effective_memory_mb
from core.serving.continuous_batcher import ContinuousBatcher
from core.serving.token_stream import stream_tokens
from core.storage.jsonl_store import JSONLStore
from core.telemetry.otel_exporter import export_otel_spans
from core.telemetry.queue_writer import AsyncQueueWriter
from core.transformers.attention import simulate_attention

TRACE_PATH = "./data/traces/traces.jsonl"
ROLLUP_PATH = "./data/metrics/rollups.jsonl"


class InferRequest(BaseModel):
    prompt: str = Field(min_length=1)


class DistributedInferRequest(BaseModel):
    prompt: str = Field(min_length=1)
    retries: int = Field(default=2, ge=0, le=5)


class DistributedLoadRequest(BaseModel):
    prompt: str = "distributed synthetic load"
    count: int = Field(default=100, ge=1, le=10000)
    retries: int = Field(default=1, ge=0, le=5)


class KVPutRequest(BaseModel):
    key: str
    token_count: int = Field(ge=0, le=200000)


class BatchSubmitRequest(BaseModel):
    prompt: str
    quant_mode: str = "fp16"


class StreamRequest(BaseModel):
    text: str
    delay_sec: float = Field(default=0.001, ge=0.0, le=0.1)


class AttentionRequest(BaseModel):
    text: str = Field(min_length=1)
    seed: int = 42


class ActivationRequest(BaseModel):
    num_layers: int = Field(default=6, ge=1, le=64)
    hidden_dim: int = Field(default=64, ge=8, le=4096)
    seed: int = 42


class DriftRequest(BaseModel):
    v1: list[float]
    v2: list[float]


class FaultScenarioRequest(BaseModel):
    name: str = "stable"


store = JSONLStore(TRACE_PATH)
rollup_store = JSONLStore(ROLLUP_PATH)
writer = AsyncQueueWriter(store)
rollup_stop = Event()
rollup_thread: Thread | None = None

# Phase 2 components
request_queue = RequestQueue(maxsize=2000)
rr_router = RoundRobinRouter(worker_count=4)
least_router = LeastQueueRouter(worker_count=4)
dpool = DistributedWorkerPool(worker_count=4, failure_policy=FailurePolicy(timeout_rate=0.02, transient_rate=0.06))

# Phase 3 components
kv_cache = KVCacheSimulator(max_tokens=50000)
batcher = ContinuousBatcher(max_batch_size=16)


app = FastAPI(title="Future AI Systems API", version="0.4.0")


def _rollup_loop(interval_sec: int = 30) -> None:
    while not rollup_stop.is_set():
        rows = store.tail(limit=10000)
        stats = summarize(rows)
        stats["timestamp"] = datetime.now(UTC).isoformat()
        rollup_store.append(stats)
        sleep(interval_sec)


def _persist(rec: dict) -> None:
    accepted = writer.enqueue(rec)
    rec["queued"] = accepted
    if not accepted:
        store.append(rec)


@app.on_event("startup")
def on_startup() -> None:
    global rollup_thread
    writer.start()
    rollup_stop.clear()
    rollup_thread = Thread(target=_rollup_loop, daemon=True)
    rollup_thread.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    writer.stop()
    rollup_stop.set()
    if rollup_thread:
        rollup_thread.join(timeout=2)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "future-ai-systems", "phase": "all"}


@app.post("/infer")
def infer(payload: InferRequest) -> dict:
    rec = run_inference(payload.prompt).model_dump()
    _persist(rec)
    return rec


@app.post("/distributed/infer")
def distributed_infer(payload: DistributedInferRequest) -> dict:
    rr_target = rr_router.route()
    queue_depths = [request_queue.depth()] * dpool.worker_count
    least_target = least_router.route(queue_depths)

    queued = request_queue.submit({"prompt": payload.prompt})
    rec = dpool.infer(payload.prompt, retries=payload.retries)
    rec["routing"] = {
        "round_robin_target": rr_target,
        "least_queue_target": least_target,
        "queued": queued,
    }
    _persist(rec)
    return rec


@app.post("/distributed/load")
def distributed_load(payload: DistributedLoadRequest) -> dict:
    success = 0
    failed = 0

    for _ in range(payload.count):
        rr_router.route()
        queue_depths = [request_queue.depth()] * dpool.worker_count
        least_router.route(queue_depths)
        request_queue.submit({"prompt": payload.prompt})
        rec = dpool.infer(payload.prompt, retries=payload.retries)
        if rec.get("status") == "error":
            failed += 1
        else:
            success += 1
        _persist(rec)

    return {
        "requested": payload.count,
        "success": success,
        "failed": failed,
        "worker_metrics": dpool.metrics(),
    }


@app.get("/distributed/metrics")
def distributed_metrics() -> dict:
    return {
        "worker_pool": dpool.metrics(),
        "queue": {
            "depth": request_queue.depth(),
            "submitted": request_queue.stats.submitted,
            "rejected": request_queue.stats.rejected,
        },
        "router": {
            "round_robin_routed_total": rr_router.stats.routed_total,
            "least_queue_routed_total": least_router.stats.routed_total,
        },
    }


@app.get("/distributed/fault/scenarios")
def fault_scenarios() -> dict:
    return {"scenarios": scenario_names()}


@app.post("/distributed/fault/scenario")
def set_fault_scenario(payload: FaultScenarioRequest) -> dict:
    s = get_scenario(payload.name)
    dpool.failure_policy.timeout_rate = s.timeout_rate
    dpool.failure_policy.transient_rate = s.transient_rate
    return {
        "active_scenario": s.name,
        "timeout_rate": s.timeout_rate,
        "transient_rate": s.transient_rate,
    }


# ------------------ Phase 3 APIs ------------------
@app.get("/phase3/kv/{key}")
def kv_get(key: str) -> dict:
    return {"key": key, "cached_tokens": kv_cache.lookup(key), "metrics": kv_cache.metrics()}


@app.post("/phase3/kv")
def kv_put(payload: KVPutRequest) -> dict:
    kv_cache.put(payload.key, payload.token_count)
    return {"status": "ok", "metrics": kv_cache.metrics()}


@app.get("/phase3/kv/metrics")
def kv_metrics() -> dict:
    m = kv_cache.metrics()
    m["estimated_kv_memory_mb"] = estimate_kv_memory_mb(m["tokens_stored"])  # fp16-like baseline
    return m


@app.post("/phase3/batch/submit")
def batch_submit(payload: BatchSubmitRequest) -> dict:
    accepted = batcher.submit(payload.model_dump())
    return {"accepted": accepted, "batcher": batcher.metrics()}


@app.post("/phase3/batch/flush")
def batch_flush() -> dict:
    batch = batcher.next_batch()
    outputs: list[dict] = []

    for req in batch:
        rec = run_inference(req["prompt"]).model_dump()
        rec["quant_mode"] = req.get("quant_mode", "fp16")
        rec["memory_mb_effective"] = effective_memory_mb(float(rec.get("memory_mb", 0.0)), rec["quant_mode"])
        _persist(rec)
        outputs.append(rec)

    return {
        "batch_size": len(batch),
        "batcher": batcher.metrics(),
        "results": outputs,
    }


@app.post("/phase3/stream")
def phase3_stream(payload: StreamRequest) -> dict:
    toks = list(stream_tokens(payload.text, delay_sec=payload.delay_sec))
    return {
        "token_count": len(toks),
        "tokens": toks,
        "avg_tokens_per_sec": round((len(toks) / max(0.001, len(toks) * payload.delay_sec)), 3),
    }


@app.get("/phase3/metrics")
def phase3_metrics() -> dict:
    kv = kv_cache.metrics()
    return {
        "kv_cache": kv,
        "kv_estimated_memory_mb": estimate_kv_memory_mb(kv["tokens_stored"]),
        "batcher": batcher.metrics(),
    }


# ------------------ Remaining module APIs ------------------
@app.post("/transformers/attention")
def attention_map(payload: AttentionRequest) -> dict:
    tokens = payload.text.split()
    attn = simulate_attention(tokens=tokens, seed=payload.seed)
    return {
        "tokens": attn.tokens,
        "attention_matrix": attn.attention_matrix,
        "entropy_per_token": attn.entropy_per_token,
    }


@app.post("/activations/extract")
def activations_extract(payload: ActivationRequest) -> dict:
    return synthetic_activations(num_layers=payload.num_layers, hidden_dim=payload.hidden_dim, seed=payload.seed)


@app.post("/activations/drift")
def activations_drift(payload: DriftRequest) -> dict:
    return {"drift_score": activation_drift_score(payload.v1, payload.v2)}


@app.get("/otel/spans")
def otel_spans(limit: int = 200, service_name: str = "future-ai-systems") -> list[dict]:
    rows = store.tail(limit=max(1, min(limit, 10000)))
    return export_otel_spans(rows, service_name=service_name)


@app.get("/traces")
def traces(limit: int = 100) -> list[dict]:
    return store.tail(limit=max(1, min(limit, 10000)))


@app.get("/trace/{trace_id}")
def trace(trace_id: str) -> list[dict]:
    rows = store.tail(limit=10000)
    return [r for r in rows if r.get("trace_id") == trace_id]


@app.get("/analytics")
def analytics(limit: int = 5000) -> dict:
    rows = store.tail(limit=max(1, min(limit, 100000)))
    return summarize(rows)


@app.get("/metrics/queue")
def queue_metrics() -> dict:
    return writer.metrics()


@app.get("/metrics/rollups")
def rollups(limit: int = 100) -> list[dict]:
    return rollup_store.tail(limit=max(1, min(limit, 1000)))
