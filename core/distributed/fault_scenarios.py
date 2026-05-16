from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScenarioConfig:
    name: str
    timeout_rate: float
    transient_rate: float


SCENARIOS = {
    "stable": ScenarioConfig("stable", timeout_rate=0.01, transient_rate=0.02),
    "degraded": ScenarioConfig("degraded", timeout_rate=0.05, transient_rate=0.12),
    "incident": ScenarioConfig("incident", timeout_rate=0.12, transient_rate=0.20),
}


def scenario_names() -> list[str]:
    return list(SCENARIOS.keys())


def get_scenario(name: str) -> ScenarioConfig:
    return SCENARIOS.get(name, SCENARIOS["stable"])
