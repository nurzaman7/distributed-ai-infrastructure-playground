from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock

from core.distributed.failure import FailurePolicy, maybe_fail
from core.distributed.retry import retry_transient
from core.inference.simulator import run_inference


@dataclass
class WorkerStats:
    submitted: int = 0
    completed: int = 0
    failed: int = 0


class DistributedWorkerPool:
    def __init__(self, worker_count: int = 4, failure_policy: FailurePolicy | None = None) -> None:
        self.worker_count = worker_count
        self.failure_policy = failure_policy or FailurePolicy()
        self.exec = ThreadPoolExecutor(max_workers=worker_count)
        self.stats = WorkerStats()
        self._lock = Lock()

    def infer(self, prompt: str, retries: int = 2) -> dict:
        with self._lock:
            self.stats.submitted += 1

        def task() -> dict:
            maybe_fail(self.failure_policy)
            return run_inference(prompt).model_dump()

        try:
            result = retry_transient(task, retries=retries)
            with self._lock:
                self.stats.completed += 1
            result["distributed"] = True
            return result
        except Exception as exc:
            with self._lock:
                self.stats.failed += 1
            return {
                "distributed": True,
                "status": "error",
                "error": str(exc),
                "input": prompt,
                "output": "",
                "latency_ms": 0.0,
                "tokens_in": len(prompt.split()),
                "tokens_out": 0,
                "memory_mb": 0.0,
                "trace_id": "",
                "span_id": "",
            }

    def metrics(self) -> dict:
        with self._lock:
            return {
                "workers": self.worker_count,
                "submitted": self.stats.submitted,
                "completed": self.stats.completed,
                "failed": self.stats.failed,
            }
