"""指标越界：超出该指标的参考区间就标出来。"""

from __future__ import annotations

from datetime import date

from ..models import Finding, Metric

PENALTY = 4


def ranges_from(data: dict) -> dict[str, tuple[float, float, str]]:
    return {k: (v[0], v[1], v[2]) for k, v in data.items()}


def out_of_range(
    metrics: list[Metric], ranges: dict[str, tuple[float, float, str]]
) -> list[Finding]:
    out: list[Finding] = []
    for m in metrics:
        ref = ranges.get(m.name)
        if not ref:
            continue
        low, high, unit = ref
        if m.value < low or m.value > high:
            out.append(
                Finding(
                    "metric.out_of_range",
                    f"{m.name} {m.value:g}{m.unit} 超出参考 {low:g}-{high:g}{unit}（{m.taken_on}）",
                    PENALTY,
                    m.name,
                )
            )
    return out


def latest(metrics: list[Metric], name: str) -> Metric | None:
    rows = [m for m in metrics if m.name == name]
    return max(rows, key=lambda m: m.taken_on) if rows else None


def in_period(metrics: list[Metric], start: date, end: date) -> list[Metric]:
    return [m for m in metrics if start <= m.taken_on <= end]
