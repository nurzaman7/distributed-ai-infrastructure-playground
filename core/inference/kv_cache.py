from __future__ import annotations

from dataclasses import dataclass
from threading import Lock


@dataclass
class KVStats:
    tokens_stored: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0


class KVCacheSimulator:
    """Simple token-level KV cache simulator.

    Keys are prompt hashes; values are token counts. Capacity is token budget.
    """

    def __init__(self, max_tokens: int = 50000) -> None:
        self.max_tokens = max_tokens
        self.store: dict[str, int] = {}
        self.order: list[str] = []
        self.stats = KVStats()
        self._lock = Lock()

    def lookup(self, key: str) -> int:
        with self._lock:
            if key in self.store:
                self.stats.hits += 1
                return self.store[key]
            self.stats.misses += 1
            return 0

    def put(self, key: str, token_count: int) -> None:
        token_count = max(0, token_count)
        with self._lock:
            if key in self.store:
                self.stats.tokens_stored -= self.store[key]
                self.order.remove(key)
            self.store[key] = token_count
            self.order.append(key)
            self.stats.tokens_stored += token_count
            self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        while self.stats.tokens_stored > self.max_tokens and self.order:
            k = self.order.pop(0)
            self.stats.tokens_stored -= self.store.get(k, 0)
            self.store.pop(k, None)
            self.stats.evictions += 1

    def metrics(self) -> dict:
        with self._lock:
            return {
                "max_tokens": self.max_tokens,
                "entries": len(self.store),
                "tokens_stored": self.stats.tokens_stored,
                "hits": self.stats.hits,
                "misses": self.stats.misses,
                "evictions": self.stats.evictions,
            }
