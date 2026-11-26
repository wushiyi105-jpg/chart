"""缺数据：最近 7 天一条指标都没有，就写"未记录"。"""

from __future__ import annotations

from datetime import date

from ..models import Finding, Metric

PENALTY = 2
WINDOW = 7


def missing(metrics: list[Metric], today: date) -> list[Finding]:
    recent = [m for m in metrics if (today - m.taken_on).days <= WINDOW]
    if recent:
        return []
    label = metrics[-1].taken_on.isoformat() if metrics else "无"
    return [Finding("data.missing", f"最近 {WINDOW} 天未记录（最后一次 {label}）", PENALTY, "metrics")]
