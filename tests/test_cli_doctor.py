from __future__ import annotations

from typer.testing import CliRunner

from chart.doctor import run_doctor
from chart.iface.cli import app


def test_doctor_green(settings):
    checks, ok = run_doctor(settings)
    assert ok is True


def test_cli_summary_ok(tmp_path):
    db = str(tmp_path / "c.db")
    res = CliRunner().invoke(app, ["summary", "--db", db, "--day", "2026-11-27"])
    assert res.exit_code == 0
    assert "指标" in res.output


def test_cli_bad_day_exits_non_zero(tmp_path):
    res = CliRunner().invoke(app, ["summary", "--db", str(tmp_path / "c.db"), "--day", "2026-13-40"])
    assert res.exit_code != 0
