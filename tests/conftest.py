from __future__ import annotations

import pytest

from chart.adapters.store import SqliteStore
from chart.config import Settings


@pytest.fixture()
def store(tmp_path) -> SqliteStore:
    return SqliteStore(tmp_path / "t.db")


@pytest.fixture()
def settings(tmp_path) -> Settings:
    return Settings(db_path=tmp_path / "t.db", llm_api_key="", port=8012)


@pytest.fixture()
def ranges():
    return {
        "血压高压": (90.0, 139.0, "mmHg"),
        "空腹血糖": (3.9, 6.1, "mmol/L"),
        "体重": (45.0, 65.0, "kg"),
    }
