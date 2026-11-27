"""本地聚合：指标区间、依从、复诊、缺数据。"""

from __future__ import annotations

from datetime import date, timedelta

from .guard import NUM
from .models import Med, Metric, Summary, Visit
from .rules.adherence import missed, rate
from .rules.metrics import latest, out_of_range
from .rules.missing import missing
from .rules.visits import overdue

QUESTIONS = [
    "现在的用药需要调整剂量吗",
    "下次复诊安排在什么时候",
    "这些指标里哪一项最需要盯",
    "需要补做哪些检查",
]


def build(
    metrics: list[Metric],
    meds: list[Med],
    visits: list[Visit],
    ranges: dict[str, tuple[float, float, str]],
    today: date,
    cycle_days: int = 90,
) -> Summary:
    start = today - timedelta(days=90)
    period = f"{start} ~ {today}"
    findings = out_of_range(metrics, ranges)
    findings += missed(meds, today)
    findings += overdue(visits, cycle_days, today)
    findings += missing(metrics, today)

    rows: list[str] = []
    for name in ranges:
        m = latest(metrics, name)
        if m is None:
            rows.append(f"{name}：未记录")
            continue
        low, high, unit = ranges[name]
        flag = "（超参考）" if (m.value < low or m.value > high) else ""
        rows.append(f"{name} {m.value:g}{m.unit}（{m.taken_on}）{flag}")

    med_rows = [
        f"{m.name} {m.dose}，每日 {m.per_day} 次，依从 {rate(m, today):.0%}"
        for m in meds
    ]
    visit_rows = [
        f"{v.on} {v.doctor}" + (f"：{v.notes}" if v.notes else "") for v in visits
    ]
    allowed: set[str] = set()

    def allow(text: str) -> None:
        allowed.update(NUM.findall(text))

    allow(period)
    for m in metrics:
        allow(f"{m.value:g}")
        allow(m.taken_on.isoformat())
    for med in meds:
        allow(med.dose)
        allow(str(med.per_day))
        allow(f"{rate(med, today):.0%}")
        allow(med.start.isoformat())
        allow(med.end.isoformat())
    for v in visits:
        allow(v.on.isoformat())
    for low, high, _ in ranges.values():
        allow(f"{low:g}")
        allow(f"{high:g}")

    return Summary(
        period=period,
        metrics=rows,
        meds=med_rows,
        visits=visit_rows,
        questions=list(QUESTIONS),
        findings=findings,
        allowed=allowed,
    )
