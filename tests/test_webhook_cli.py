from __future__ import annotations

from typer.testing import CliRunner

import chart.iface.cli as cli
from chart.iface.cli import app


def _seed(db: str) -> None:
    assert CliRunner().invoke(app, ["seed", "--db", db]).exit_code == 0


def test_compose_pushes_webhook(tmp_path, monkeypatch):
    db = str(tmp_path / "w.db")
    _seed(db)
    monkeypatch.setattr(cli.default_settings, "llm_api_key", "")
    monkeypatch.setattr(cli.default_settings, "webhook_url", "http://hook.test/chart")

    sent = []

    class Fake:
        def __init__(self, url):
            self.url = url

        def send(self, text):
            sent.append((self.url, text))
            return True

    monkeypatch.setattr(cli, "WebhookNotifier", Fake)
    res = CliRunner().invoke(app, ["compose", "--db", db, "--day", "2026-11-27"])
    assert res.exit_code == 0, res.output
    assert sent and sent[0][0] == "http://hook.test/chart" and sent[0][1].strip()
    assert "webhook ok" in res.output
