from __future__ import annotations

from time import sleep
from typing import Callable, TypeVar

from core.distributed.failure import SimulatedTransientError

T = TypeVar("T")


def retry_transient(fn: Callable[[], T], retries: int = 2, backoff_sec: float = 0.02) -> T:
    attempt = 0
    while True:
        try:
            return fn()
        except SimulatedTransientError:
            if attempt >= retries:
                raise
            sleep(backoff_sec * (2**attempt))
            attempt += 1
