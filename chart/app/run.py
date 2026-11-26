"""用例：取记录 → 聚合 → 模型写摘要 → 双重守卫 → 导出。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from ..adapters.llm import build_llm
from ..adapters.store import SqliteStore
from ..config import Settings
from ..domain.engine import build
from ..domain.guard import check
from ..domain.models import Summary
from ..domain.render import render

PROMPT = """你在整理一份给医生看的病程摘要。只允许陈述记录里的事实：
指标名与数值、用药与依从率、复诊日期、患者自述。
禁止写任何判断或建议：不写"建议""诊断""可能是""考虑""疑似""推荐"。
每一条都必须能在输入里找到对应记录。输出五段：## 指标 / ## 用药 / ## 复诊 / ## 想问医生。"""


def ranges(store: SqliteStore) -> dict[str, tuple[float, float, str]]:
    seed = Path(__file__).resolve().parents[2] / "data" / "ranges.json"
    return store.ranges(seed)


def build_for(store: SqliteStore, settings: Settings, today: date | None = None) -> Summary:
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


def compose(store: SqliteStore, settings: Settings, today: date | None = None) -> tuple[Summary, str]:
    summary = build_for(store, settings, today)
    allowed = allowed_numbers(summary)
    text = summary.body
    if settings.llm_enabled:
        llm = build_llm(settings.llm_base_url, settings.llm_api_key, settings.llm_model, PROMPT)
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
