from __future__ import annotations

from datetime import date

from chart.domain.models import Metric, Visit
from chart.domain.rules.missing import missing
from chart.domain.rules.visits import overdue


def test_overdue_visit_flagged():
    visits = [Visit(1, date(2026, 8, 1), "王医生", "")]
    findings = overdue(visits, 90, date(2026, 11, 27))
    assert findings[0].rule_id == "visit.overdue"
    assert "118 天" in findings[0].message


def test_recent_visit_not_flagged():
    visits = [Visit(1, date(2026, 10, 8), "王医生", "")]
    assert overdue(visits, 90, date(2026, 11, 27)) == []


def test_missing_data_says_untracked():
    metrics = [Metric(1, "体重", 58.4, "kg", date(2026, 11, 1))]
    findings = missing(metrics, date(2026, 11, 27))
    assert findings[0].rule_id == "data.missing"
    assert "未记录" in findings[0].message


def test_recent_metric_no_missing():
    metrics = [Metric(1, "体重", 58.4, "kg", date(2026, 11, 25))]
    assert missing(metrics, date(2026, 11, 27)) == []
