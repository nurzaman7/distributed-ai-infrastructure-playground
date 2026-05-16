from __future__ import annotations

import json
from pathlib import Path


class JSONLStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, row: dict) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

    def tail(self, limit: int = 100) -> list[dict]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        out: list[dict] = []
        for ln in lines[-limit:]:
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
        return out
