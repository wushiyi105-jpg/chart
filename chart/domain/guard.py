"""双重守卫：数字可回查；出现判断词整行丢弃。"""

from __future__ import annotations

import re

from .models import Finding

NUM = re.compile(r"[0-9]+(?:\.[0-9]+)?%?")
BANNED = ("建议", "诊断", "可能是", "考虑", "疑似", "应该是", "推荐")
PENALTY_NUM = 8
PENALTY_WORD = 10


def check(text: str, allowed: set[str]) -> tuple[str, list[Finding]]:
    kept: list[str] = []
    findings: list[Finding] = []
    for line in text.splitlines():
        word = next((w for w in BANNED if w in line), None)
        if word:
            findings.append(
                Finding("guard.diagnosis", f"整行丢弃：出现「{word}」", PENALTY_WORD, line[:40])
            )
            continue
        bad = [n for n in NUM.findall(line) if n not in allowed]
        if bad:
            findings.append(
                Finding("guard.number", f"整行丢弃：数字 {sorted(bad)} 不在记录里", PENALTY_NUM, line[:40])
            )
            continue
        kept.append(line)
    return "\n".join(kept).strip(), findings
