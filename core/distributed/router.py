from __future__ import annotations

from dataclasses import dataclass
from random import randint


@dataclass
class RouterStats:
    routed_total: int = 0


class RoundRobinRouter:
    def __init__(self, worker_count: int) -> None:
        self.worker_count = max(1, worker_count)
        self._idx = 0
        self.stats = RouterStats()

    def route(self) -> int:
        target = self._idx
        self._idx = (self._idx + 1) % self.worker_count
        self.stats.routed_total += 1
        return target


class LeastQueueRouter:
    def __init__(self, worker_count: int) -> None:
        self.worker_count = max(1, worker_count)
        self.stats = RouterStats()

    def route(self, queue_depths: list[int]) -> int:
        if not queue_depths:
            return randint(0, self.worker_count - 1)
        min_depth = min(queue_depths)
        idx = queue_depths.index(min_depth)
        self.stats.routed_total += 1
        return idx
