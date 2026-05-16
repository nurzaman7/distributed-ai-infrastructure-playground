from __future__ import annotations

from dataclasses import dataclass
from queue import Queue
from threading import Lock


@dataclass
class BatchStats:
    submitted: int = 0
    formed_batches: int = 0


class ContinuousBatcher:
    def __init__(self, max_batch_size: int = 16) -> None:
        self.max_batch_size = max(1, max_batch_size)
        self.q: Queue[dict] = Queue(maxsize=10000)
        self.stats = BatchStats()
        self._lock = Lock()

    def submit(self, req: dict) -> bool:
        if self.q.full():
            return False
        self.q.put_nowait(req)
        with self._lock:
            self.stats.submitted += 1
        return True

    def next_batch(self) -> list[dict]:
        out: list[dict] = []
        while len(out) < self.max_batch_size and not self.q.empty():
            out.append(self.q.get_nowait())
        if out:
            with self._lock:
                self.stats.formed_batches += 1
        return out

    def metrics(self) -> dict:
        with self._lock:
            return {
                "queue_depth": self.q.qsize(),
                "max_batch_size": self.max_batch_size,
                "submitted": self.stats.submitted,
                "formed_batches": self.stats.formed_batches,
            }
