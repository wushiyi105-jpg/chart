from __future__ import annotations

from datetime import date

from chart.domain.models import Med
from chart.domain.rules.adherence import expected, missed, rate


def _med(taken: int, per_day: int = 2, start="2026-08-20", end="2026-11-30") -> Med:
    return Med(1, "二甲双胍", "0.5g", per_day, date.fromisoformat(start), date.fromisoformat(end), taken)


def test_expected_counts_inclusive_days():
    assert expected(_med(0), date(2026, 11, 30)) == 103


def test_rate_full_when_enough():
    assert rate(_med(206), date(2026, 11, 30)) == 1.0


def test_low_adherence_flagged_with_rule_id():
    findings = missed([_med(120)], date(2026, 11, 30))
    assert findings[0].rule_id == "adherence.missed"
    assert "依从" in findings[0].message


def test_good_adherence_no_finding():
    assert missed([_med(206)], date(2026, 11, 30)) == []
