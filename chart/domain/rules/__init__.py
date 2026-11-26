"""每条规则一个扣分，测试逐条断言 rule_id。"""

RULES = {
    "metric.out_of_range": 4,
    "adherence.missed": 5,
    "visit.overdue": 3,
    "data.missing": 2,
    "guard.number": 8,
    "guard.diagnosis": 10,
}
