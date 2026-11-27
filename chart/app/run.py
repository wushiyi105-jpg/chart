"""用例：取记录 → 聚合 → 模型写摘要 → 双重守卫 → 导出。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from ..config import Settings
from ..domain.engine import build
from ..domain.guard import check
from ..domain.models import Summary
from ..domain.render import render
from ..ports import LLMPort, StorePort

PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "summary.md").read_text(encoding="utf-8")


def ranges(store: StorePort) -> dict[str, tuple[float, float, str]]:
    seed = Path(__file__).resolve().parents[2] / "data" / "ranges.json"
    return store.ranges(seed)


def build_for(store: StorePort, settings: Settings, today: date | None = None) -> Summary:
    today = today or date.today()
    summary = build(
        store.list_metrics(today.replace(year=today.year - 1)),
        store.list_meds(),
        store.list_visits(),
        ranges(store),
        today,
        cycle_days=settings.visit_cycle_days,
    )
    summary.body = render(summary)
    return summary


def allowed_numbers(summary: Summary) -> set[str]:
    from ..domain.guard import NUM

    text = "\n".join(summary.metrics + summary.meds + summary.visits + summary.questions)
    return set(NUM.findall(text))


def compose(
    store: StorePort, settings: Settings, today: date | None = None, llm: LLMPort | None = None
) -> tuple[Summary, str]:
    summary = build_for(store, settings, today)
    allowed = allowed_numbers(summary)
    text = summary.body
    if llm is not None:
        facts = f"period={summary.period}\n" + "\n".join(
            summary.metrics + summary.meds + summary.visits
        )
        try:
            raw = llm.write(PROMPT, facts)
        except Exception:  # noqa: BLE001 模型失败不挡住导出
            raw = ""
        if raw:
            guarded, findings = check(raw, allowed)
            summary.findings.extend(findings)
            if guarded.strip():
                text = guarded
    return summary, text
