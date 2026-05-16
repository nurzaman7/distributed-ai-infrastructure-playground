from __future__ import annotations

from dataclasses import dataclass
from random import random


@dataclass
class FailurePolicy:
    timeout_rate: float = 0.03
    transient_rate: float = 0.05


class SimulatedTimeoutError(RuntimeError):
    pass


class SimulatedTransientError(RuntimeError):
    pass


def maybe_fail(policy: FailurePolicy) -> None:
    r = random()
    if r < policy.timeout_rate:
        raise SimulatedTimeoutError("simulated worker timeout")
    if r < policy.timeout_rate + policy.transient_rate:
        raise SimulatedTransientError("simulated transient failure")
