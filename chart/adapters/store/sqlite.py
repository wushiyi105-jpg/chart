"""SQLite：episodes / metrics / meds / visits。"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from sqlalchemy import Date, Float, Integer, String, Text, inspect, select
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from ...domain.models import Med, Metric, Visit
from .base import Base, make_engine, make_session


class MetricRow(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(16), default="")
    taken_on: Mapped[date] = mapped_column(Date)


class MedRow(Base):
    __tablename__ = "meds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    dose: Mapped[str] = mapped_column(String(40), default="")
    per_day: Mapped[int] = mapped_column(Integer, default=1)
    start: Mapped[date] = mapped_column(Date)
    end: Mapped[date] = mapped_column(Date)
    taken: Mapped[int] = mapped_column(Integer, default=0)


class VisitRow(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    on: Mapped[date] = mapped_column(Date)
    doctor: Mapped[str] = mapped_column(String(60), default="")
    notes: Mapped[str] = mapped_column(Text, default="")


class EpisodeRow(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    start: Mapped[date] = mapped_column(Date)
    end: Mapped[date | None] = mapped_column(Date, nullable=True)
    severity: Mapped[str] = mapped_column(String(12), default="mild")


class SqliteStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.engine = make_engine(self.path)
        self.session: sessionmaker[Session] = make_session(self.engine)
        self.init_schema()

    def init_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def schema_ok(self) -> bool:
        return {"metrics", "meds", "visits", "episodes"} <= set(
            inspect(self.engine).get_table_names()
        )

    def summary(self) -> str:
        return f"{len(self.list_metrics())} 条指标、{len(self.list_meds())} 种用药"

    def add_metric(self, name: str, value: float, unit: str, taken_on: date) -> int:
        if value <= 0:
            raise ValueError("指标值必须为正")
        with self.session() as s:
            row = MetricRow(name=name, value=value, unit=unit, taken_on=taken_on)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_metrics(self, since: date | None = None) -> list[Metric]:
        with self.session() as s:
            stmt = select(MetricRow)
            if since:
                stmt = stmt.where(MetricRow.taken_on >= since)
            rows = s.scalars(stmt.order_by(MetricRow.taken_on)).all()
        return [Metric(r.id, r.name, r.value, r.unit, r.taken_on) for r in rows]

    def add_med(self, name: str, dose: str, per_day: int, start: date, end: date, taken: int) -> int:
        with self.session() as s:
            row = MedRow(name=name, dose=dose, per_day=per_day, start=start, end=end, taken=taken)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_meds(self) -> list[Med]:
        with self.session() as s:
            rows = s.scalars(select(MedRow)).all()
        return [Med(r.id, r.name, r.dose, r.per_day, r.start, r.end, r.taken) for r in rows]

    def add_visit(self, on: date, doctor: str, notes: str = "") -> int:
        with self.session() as s:
            row = VisitRow(on=on, doctor=doctor, notes=notes)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_visits(self) -> list[Visit]:
        with self.session() as s:
            rows = s.scalars(select(VisitRow).order_by(VisitRow.on)).all()
        return [Visit(r.id, r.on, r.doctor, r.notes) for r in rows]

    def add_episode(self, title: str, start: date, end: date | None, severity: str = "mild") -> int:
        with self.session() as s:
            row = EpisodeRow(title=title, start=start, end=end, severity=severity)
            s.add(row)
            s.commit()
            return int(row.id)

    def ranges(self, path: Path) -> dict[str, tuple[float, float, str]]:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {k: (v[0], v[1], v[2]) for k, v in data["ranges"].items()}

