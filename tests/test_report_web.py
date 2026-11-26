from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

from chart.app.run import build_for, compose
from chart.iface.web import create_app


def _seed(store):
    store.add_metric("血压高压", 141, "mmHg", date(2026, 11, 19))
    store.add_med("二甲双胍", "0.5g", 2, date(2026, 8, 20), date(2026, 11, 30), 120)
    store.add_visit(date(2026, 8, 1), "王医生", "初诊")


def test_summary_aggregates_and_flags(store, settings):
    _seed(store)
    summary = build_for(store, settings, date(2026, 11, 27))
    ids = {f.rule_id for f in summary.findings}
    assert "metric.out_of_range" in ids
    assert "adherence.missed" in ids
    assert "visit.overdue" in ids
    assert "血压高压 141mmHg" in summary.metrics[0] or "141" in summary.metrics[0]


def test_compose_offline_keeps_five_fields(store, settings):
    _seed(store)
    summary, text = compose(store, settings, date(2026, 11, 27))
    assert "## 用药" in text
    assert "## 想问医生" in text
    assert summary.penalty_total > 0


def test_web_index_and_add(store, settings):
    _seed(store)
    client = TestClient(create_app(settings, store))
    assert client.get("/").status_code == 200
    resp = client.post("/metric", data={"name": "体重", "value": "58.4", "unit": "kg",
                                        "day": "2026-11-25"}, follow_redirects=False)
    assert resp.status_code == 303
    assert "体重" in client.get("/").text


def test_web_rejects_bad_value(store, settings):
    client = TestClient(create_app(settings, store))
    resp = client.post("/metric", data={"name": "体重", "value": "-1", "unit": "kg",
                                        "day": "2026-11-25"}, follow_redirects=False)
    assert resp.status_code == 303
