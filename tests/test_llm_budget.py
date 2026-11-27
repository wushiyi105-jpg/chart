from __future__ import annotations

from chart.adapters.llm import build_llm
from chart.config import Settings


def test_llm_budget_defaults_to_20s_once():
    s = Settings()
    assert s.llm_timeout == 20.0
    client = build_llm("http://127.0.0.1:11434/v1", "x", "qwen2.5:1.5b", "sys")
    assert client.timeout == 20.0
    assert client.retries == 1
    assert client.max_tokens == 2000
