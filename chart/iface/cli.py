"""命令行：seed / metric / summary / compose / doctor / serve。"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import typer
from rich.console import Console

from ..adapters.store import SqliteStore
from ..app.run import build_for, compose
from ..config import Settings
from ..config import settings as default_settings
from ..doctor import main as doctor_main

app = typer.Typer(help="病程记录：三个月压成一页", no_args_is_help=True)
console = Console()


def _settings(db: Path | None, port: int | None = None) -> Settings:
    s = default_settings.model_copy(deep=True)
    if db:
        s.db_path = db
    if port:
        s.port = port
    return s


def _store(settings: Settings) -> SqliteStore:
    return SqliteStore(settings.db_path)


@app.command()
def seed(db: Path = typer.Option(None)) -> None:
    """写入三个月的指标、用药与复诊。"""
    s = _settings(db)
    store = _store(s)
    data = json.loads(
        (Path(__file__).resolve().parents[2] / "data" / "seed.json").read_text(encoding="utf-8")
    )
    for row in data["metrics"]:
        store.add_metric(row["name"], row["value"], row["unit"], date.fromisoformat(row["on"]))
    for row in data["meds"]:
        store.add_med(
            row["name"], row["dose"], row["per_day"], date.fromisoformat(row["start"]),
            date.fromisoformat(row["end"]), row["taken"],
        )
    for row in data["visits"]:
        store.add_visit(date.fromisoformat(row["on"]), row["doctor"], row.get("notes", ""))
    console.print(
        f"已写入 {len(data['metrics'])} 条指标、{len(data['meds'])} 种用药、{len(data['visits'])} 次复诊"
    )


@app.command()
def metric(
    name: str = typer.Option(...),
    value: float = typer.Option(...),
    unit: str = typer.Option(""),
    day: str = typer.Option("", help="YYYY-MM-DD，默认今天"),
    db: Path = typer.Option(None),
) -> None:
    """补一条指标。"""
    s = _settings(db)
    store = _store(s)
    try:
        store.add_metric(name, value, unit, date.fromisoformat(day) if day else date.today())
    except ValueError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=2) from exc
    console.print(f"已记：{name} {value:g}{unit}")


@app.command()
def summary(day: str = typer.Option("", help="以哪天为终点"), db: Path = typer.Option(None)) -> None:
    """看聚合结果与扣分。"""
    s = _settings(db)
    d = date.fromisoformat(day) if day else date.today()
    summary_obj = build_for(_store(s), s, d)
    console.print(summary_obj.body)
    if summary_obj.findings:
        console.print("扣分：")
        for f in summary_obj.findings:
            console.print(f"  [yellow]{f.rule_id}[/] -{f.penalty} {f.message}")
    console.print(f"合计扣分 {summary_obj.penalty_total}")


@app.command("compose")
def compose_cmd(day: str = typer.Option(""), db: Path = typer.Option(None)) -> None:
    """成文（有 key 走模型，否则离线）。"""
    s = _settings(db)
    d = date.fromisoformat(day) if day else date.today()
    _, text = compose(_store(s), s, d)
    console.print(text)




@app.command()
def doctor(db: Path = typer.Option(None)) -> None:
    """四项体检。"""
    raise typer.Exit(code=doctor_main(_settings(db)))


@app.command()
def serve(port: int = typer.Option(None), db: Path = typer.Option(None)) -> None:
    """Web 界面。"""
    import uvicorn

    from .web import create_app

    s = _settings(db, port)
    uvicorn.run(create_app(s), host="127.0.0.1", port=s.port)


if __name__ == "__main__":
    app()
