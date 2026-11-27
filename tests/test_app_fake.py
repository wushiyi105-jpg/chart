"""真实内存 Store 跑 build_for：不建 SQLite，mypy 校验 StorePort。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from chart.app.run import allowed_numbers, build_for
from chart.config import Settings
from chart.domain.models import Med, Metric, Visit
from chart.ports import StorePort


class InMemoryStore:
    def __init__(self) -> None:
        self.metrics: list[Metric] = []
        self.meds: list[Med] = []
        self.visits: list[Visit] = []

    def list_metrics(self, since: date | None = None) -> list[Metric]:
        return self.metrics

    def list_meds(self) -> list[Med]:
        return self.meds

    def list_visits(self) -> list[Visit]:
        return self.visits

    def ranges(self, path: Path) -> dict[str, tuple[float, float, str]]:
        return {"血压": (90.0, 140.0, "mmHg")}


def test_build_for_with_memory_store(tmp_path) -> None:
    store: StorePort = InMemoryStore()
    out = build_for(store, Settings(db_path=tmp_path / "x.db"), date(2026, 1, 5))
    assert out.body
    assert not (tmp_path / "x.db").exists()
    out.body += "\n999"
    assert "999" not in allowed_numbers(out)
    assert "90" in allowed_numbers(out)
