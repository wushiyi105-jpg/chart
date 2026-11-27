"""新功能：给医生的一页摘要与 30 天演示数据。"""

from __future__ import annotations

from typer.testing import CliRunner

from chart.domain.catalog import flags, ranges, symptoms
from chart.iface.cli import app


def test_catalog_counts() -> None:
    assert len(ranges()) == 45
    assert len(symptoms()) == 8
    assert len(flags()) == 7


def test_report_cli_writes_one_page(tmp_path) -> None:
    runner = CliRunner()
    db = str(tmp_path / "chart.db")
    assert runner.invoke(app, ["seed", "--db", db]).exit_code == 0
    out = tmp_path / "给医生.md"
    result = runner.invoke(app, ["report", "--db", db, "--day", "2026-11-27", "--out", str(out)])
    assert result.exit_code == 0
    body = out.read_text(encoding="utf-8")
    assert "# 给医生的一页摘要" in body
    assert "先看红线" in body
    assert "最近三次趋势" in body
    assert "8 个问题" in body


def test_demo_seed_generates_thirty_days(tmp_path) -> None:
    result = CliRunner().invoke(app, ["seed", "--db", str(tmp_path / "demo.db"), "--demo"])
    assert result.exit_code == 0
    assert "1350 条" in result.output
