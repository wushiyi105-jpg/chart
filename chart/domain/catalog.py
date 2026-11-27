"""45 项指标范围、8 个症状问题、7 条红线。"""

from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

from .models import Metric

ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def ranges() -> dict[str, list]:
    data = json.loads((ROOT / "data" / "ranges.json").read_text(encoding="utf-8"))
    return data["ranges"]


@lru_cache(maxsize=1)
def symptoms() -> list[dict[str, str]]:
    return json.loads((ROOT / "data" / "symptoms.json").read_text(encoding="utf-8"))["symptoms"]


@lru_cache(maxsize=1)
def flags() -> list[dict[str, Any]]:
    return json.loads((ROOT / "data" / "red_flags.json").read_text(encoding="utf-8"))["flags"]


def latest_by_name(metrics: list[Metric]) -> dict[str, Metric]:
    out: dict[str, Metric] = {}
    for m in sorted(metrics, key=lambda x: x.taken_on):
        out[m.name] = m
    return out


def history(metrics: list[Metric], name: str, limit: int = 3) -> list[Metric]:
    rows = [m for m in metrics if m.name == name]
    rows.sort(key=lambda x: x.taken_on)
    return rows[-limit:]


def abnormal(metrics: list[Metric]) -> list[tuple[Metric, str]]:
    latest = latest_by_name(metrics)
    out: list[tuple[Metric, str]] = []
    for name, m in latest.items():
        band = ranges().get(name)
        if not band:
            continue
        low, high = float(band[0]), float(band[1])
        if m.value > high:
            out.append((m, "偏高"))
        elif m.value < low:
            out.append((m, "偏低"))
    return out


def red_flags(metrics: list[Metric]) -> list[str]:
    latest = latest_by_name(metrics)
    out: list[str] = []
    for flag in flags():
        m = latest.get(flag["metric"])
        if m is None:
            continue
        hit = m.value >= float(flag["value"]) if flag["op"] == ">=" else m.value < float(flag["value"])
        if hit:
            out.append(flag["message"])
    return out


def demo_metrics(today: date) -> list[tuple[str, float, str, date]]:
    """生成 30 天 × 45 项的演示序列，不覆盖真实记录，只用于演示模式。"""
    out: list[tuple[str, float, str, date]] = []
    for index, (name, (low, high, unit)) in enumerate(ranges().items()):
        for offset in range(30):
            day = date.fromordinal(today.toordinal() - 29 + offset)
            # 中间值上下轻微波动，血压和血糖后半段故意走高，方便看趋势。
            mid = (float(low) + float(high)) / 2
            step = (float(high) - float(low)) * (offset / 60)
            jitter = ((index * 7 + offset * 3) % 11 - 5) / 100 * (float(high) - float(low))
            value = mid + step + jitter
            if name in {"血压高压", "空腹血糖"}:
                value += (float(high) - float(low)) * 0.12
            out.append((name, round(value, 2), str(unit), day))
    return out
