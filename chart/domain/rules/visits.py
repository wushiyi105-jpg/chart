"""复诊间隔：超过该科室周期就提示。"""

from __future__ import annotations

from datetime import date

from ..models import Finding, Visit

PENALTY = 3


def overdue(visits: list[Visit], cycle_days: int, today: date) -> list[Finding]:
    if not visits:
        return []
    last = max(v.on for v in visits)
    days = (today - last).days
    if days <= cycle_days:
        return []
    return [
        Finding(
            "visit.overdue",
            f"距上次复诊 {days} 天，超过 {cycle_days} 天周期",
            PENALTY,
            visits[0].doctor,
        )
    ]
