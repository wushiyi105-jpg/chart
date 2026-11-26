"""FastAPI + Jinja2：指标录入与一页纸。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..adapters.store import SqliteStore
from ..app.run import build_for, compose
from ..config import Settings

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))


def create_app(settings: Settings, store: SqliteStore | None = None) -> FastAPI:
    app = FastAPI(title="Chart", version="1.0.0")
    store = store or SqliteStore(settings.db_path)

    def render(request: Request) -> HTMLResponse:
        summary = build_for(store, settings)
        return TEMPLATES.TemplateResponse(
            request, "index.html",
            {"summary": summary, "today": date.today().isoformat(),
             "metrics": store.list_metrics()[-8:], "meds": store.list_meds()},
        )

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return render(request)

    @app.post("/metric")
    def add_metric(
        name: str = Form(...), value: float = Form(...), unit: str = Form(""),
        day: str = Form(""),
    ) -> RedirectResponse:
        try:
            store.add_metric(name.strip(), value, unit, date.fromisoformat(day) if day else date.today())
        except ValueError:
            return RedirectResponse(url="/?error=1", status_code=303)
        return RedirectResponse(url="/", status_code=303)

    @app.post("/compose")
    def do_compose() -> RedirectResponse:
        compose(store, settings)
        return RedirectResponse(url="/", status_code=303)

    @app.get("/export.md", response_class=PlainTextResponse)
    def export_md() -> PlainTextResponse:
        summary, text = compose(store, settings)
        return PlainTextResponse(text, media_type="text/markdown; charset=utf-8")

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "metrics": len(store.list_metrics())}

    return app


def app_factory(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        from ..config import settings as default_settings

        settings = default_settings
    return create_app(settings)
