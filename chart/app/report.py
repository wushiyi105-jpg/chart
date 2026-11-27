"""给医生的一页摘要：红线、异常、三次趋势、用药、问题清单。"""

from __future__ import annotations

from datetime import date

from ..domain.catalog import abnormal, flags, history, latest_by_name, ranges, red_flags, symptoms
from ..domain.models import Summary
from ..ports import StorePort


def _fmt(m) -> str:
    return f"{m.value:g} {m.unit}"


def build_report(store: StorePort, summary: Summary, today: date) -> str:
    since = date(today.year - 1, today.month, 1)
    metrics = store.list_metrics(since)
    latest = latest_by_name(metrics)
    bad = abnormal(metrics)

    lines = [
        f"# 给医生的一页摘要 · {today.isoformat()}",
        "",
        f"> 数据范围 {since.isoformat()} 至 {today.isoformat()}；本地已核对 **{len(ranges())} 项指标**、"
        f"**{len(symptoms())} 个症状问题**、**{len(flags())} 条红线**。这不是诊断，只帮医生少问几句。",
        "",
        "## 一、先看红线",
        "",
    ]
    red = red_flags(metrics)
    if red:
        for line in red:
            lines.append(f"- **{line}**")
    else:
        lines.append("- 本次数据没有触发 7 条急症红线。")
    lines += ["", "## 二、异常指标", "", "| 指标 | 最新值 | 参考范围 | 判断 |", "| --- | ---: | --- | --- |"]
    if bad:
        for m, label in bad:
            band = ranges()[m.name]
            lines.append(f"| {m.name} | {_fmt(m)} | {band[0]}–{band[1]} {band[2]} | **{label}** |")
    else:
        lines.append("| - | - | - | 本次都在范围内 |")
    lines += ["", "## 三、最近三次趋势", ""]
    key_names = {m.name for m, _ in bad} | {"血压高压", "空腹血糖", "糖化血红蛋白", "体重"}
    shown = 0
    for name in sorted(key_names):
        rows = history(metrics, name)
        if len(rows) < 2:
            continue
        shown += 1
        seq = " → ".join(f"{m.taken_on.strftime('%m/%d')} {m.value:g}" for m in rows)
        delta = rows[-1].value - rows[0].value
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        lines.append(f"- **{name}**：{seq}（{arrow} {abs(delta):g} {rows[-1].unit}）")
    if not shown:
        lines.append("- 还没有连续两次的同一指标记录。")
    lines += ["", "## 四、用药与复诊", ""]
    lines += [f"- {x}" for x in summary.meds] or ["- 未记录用药"]
    lines += [f"- {x}" for x in summary.visits] or ["- 未记录复诊"]
    lines += ["", "## 五、今天要问医生的 8 个问题", ""]
    for s in symptoms():
        lines.append(f"- **{s['name']}**：{s['question']}")
    if summary.questions:
        lines += ["", "**系统另外提醒：**", ""]
        lines += [f"- {q}" for q in summary.questions[:5]]
    lines += [
        "",
        "---",
        "",
        f"说明：共读取 {len(latest)} 项最新指标；参考范围来自本地 ranges.json，"
        "红线只做就医提醒，不替代医生判断。",
        "",
    ]
    return "\n".join(lines)
