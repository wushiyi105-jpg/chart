from __future__ import annotations

from chart.domain.guard import check


def test_diagnosis_word_drops_line():
    text, findings = check("血压 141mmHg\n建议加药", {"141"})
    assert "建议" not in text
    assert findings[0].rule_id == "guard.diagnosis"


def test_number_not_in_records_dropped():
    text, findings = check("血糖 6.5mmol/L\n体重 61kg", {"6.5"})
    assert "61" not in text
    assert findings[0].rule_id == "guard.number"


def test_clean_lines_kept():
    text, findings = check("血压 141mmHg\n血糖 6.5mmol/L", {"141", "6.5"})
    assert text.count("\n") == 1
    assert findings == []


def test_all_lines_dropped_returns_empty():
    text, findings = check("建议观察\n可能是药物反应", set())
    assert text == ""
    assert len(findings) == 2
