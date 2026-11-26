"""离线一页纸：字段固定，缺的写"未记录"。"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Summary


def render(summary: "Summary") -> str:
    lines = [f"# 病程摘要（{summary.period}）", "", "## 近三个月指标"]
    lines += [f"- {x}" for x in summary.metrics] or ["- 未记录"]
    lines += ["", "## 用药"]
    lines += [f"- {x}" for x in summary.meds] or ["- 未记录"]
    lines += ["", "## 复诊"]
    lines += [f"- {x}" for x in summary.visits] or ["- 未记录"]
    lines += ["", "## 想问医生"]
    lines += [f"- {x}" for x in summary.questions]
    return "\n".join(lines).rstrip() + "\n"

