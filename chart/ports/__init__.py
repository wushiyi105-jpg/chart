"""端口：app 实际调用的方法集合，实现见 adapters。"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Protocol, runtime_checkable

from ..domain.models import Med, Metric, Visit


@runtime_checkable
class StorePort(Protocol):
    def list_metrics(self, since: date | None = None) -> list[Metric]: ...

    def list_meds(self) -> list[Med]: ...

    def list_visits(self) -> list[Visit]: ...

    def ranges(self, path: Path) -> dict[str, tuple[float, float, str]]: ...


@runtime_checkable
class LLMPort(Protocol):
    def write(self, system: str, facts: str) -> str: ...
