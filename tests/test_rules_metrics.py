from __future__ import annotations

from datetime import date

from chart.domain.models import Metric
from chart.domain.rules.metrics import latest, out_of_range


def _m(name="血压高压", value=150.0, day="2026-11-19"):
    return Metric(1, name, value, "mmHg", date.fromisoformat(day))


def test_high_value_flagged_with_rule_id(ranges):
    findings = out_of_range([_m()], ranges)
    assert findings[0].rule_id == "metric.out_of_range"
    assert "150" in findings[0].message


def test_in_range_silent(ranges):
    assert out_of_range([_m(value=128.0)], ranges) == []


def test_unknown_metric_ignored(ranges):
    assert out_of_range([_m(name="尿酸", value=500.0)], ranges) == []


def test_latest_picks_newest(ranges):
    rows = [Metric(1, "体重", 58.4, "kg", date(2026, 9, 1)),
            Metric(2, "体重", 59.1, "kg", date(2026, 11, 1))]
    assert latest(rows, "体重") == rows[1]
