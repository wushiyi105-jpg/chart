"""领域对象：只描述记录，不做判断。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Metric:
    id: int
    name: str
    value: float
    unit: str
    taken_on: date


@dataclass(frozen=True)
class Med:
    id: int
    name: str
    dose: str
    per_day: int
    start: date
    end: date
    taken: int


@dataclass(frozen=True)
class Visit:
    id: int
    on: date
    doctor: str
    notes: str


@dataclass
class Finding:
    rule_id: str
    message: str
    penalty: int
    target: str = ""


@dataclass
class Summary:
    period: str
    metrics: list[str] = field(default_factory=list)
    meds: list[str] = field(default_factory=list)
    visits: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    allowed: set[str] = field(default_factory=set)
    body: str = ""

    @property
    def penalty_total(self) -> int:
        return sum(f.penalty for f in self.findings)
