from __future__ import annotations

from dataclasses import dataclass
from queue import Queue


@dataclass
class QueueStats:
    submitted: int = 0
    rejected: int = 0


class RequestQueue:
    def __init__(self, maxsize: int = 1000) -> None:
        self.queue: Queue[dict] = Queue(maxsize=maxsize)
        self.stats = QueueStats()

    def submit(self, item: dict) -> bool:
        self.stats.submitted += 1
        if self.queue.full():
            self.stats.rejected += 1
            return False
        self.queue.put_nowait(item)
        return True

    def depth(self) -> int:
        return self.queue.qsize()
