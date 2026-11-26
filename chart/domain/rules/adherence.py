"""依从性：按处方天数 × 每日次数算应服，和实际次数比。"""

from __future__ import annotations

from datetime import date

from ..models import Finding, Med

PENALTY = 5
THRESHOLD = 0.8


def expected(med: Med, today: date) -> int:
    end = min(med.end, today)
    if end < med.start:
        return 0
    return (end - med.start).days + 1


def rate(med: Med, today: date) -> float:
    exp = expected(med, today) * med.per_day
    if exp <= 0:
        return 1.0
    return min(1.0, med.taken / exp)


def missed(meds: list[Med], today: date) -> list[Finding]:
    out: list[Finding] = []
    for med in meds:
        r = rate(med, today)
        if r < THRESHOLD:
            out.append(
                Finding(
                    "adherence.missed",
                    f"{med.name} 依从 {r:.0%}：应服 {expected(med, today) * med.per_day} 次，记录 {med.taken} 次",
                    PENALTY,
                    med.name,
                )
            )
    return out
