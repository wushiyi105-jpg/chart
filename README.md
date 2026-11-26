# Chart · 病程记录

[![test](https://github.com/wushiyi105-jpg/chart/workflows/test/badge.svg)](https://github.com/wushiyi105-jpg/chart/actions)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

![示例](assets/demo.gif)

三个月的指标、用药、复诊，压成一页纸给医生看。

## 为什么不是把记录丢给模型总结

模型会顺手写「建议复查」——那是医生的活。Chart 把该说的话限定在记录上：指标是否超出参考区间、
依从率多少、距上次复诊几天，全在本地算；模型只把这些事实排成医生习惯读的顺序，
写出来的每一行都要过两道守卫：数字必须在记录里、出现判断词整行删掉。

## 它做什么

1. **指标聚合**：8 个慢病指标，取最近一次，标出超出参考区间的项。
2. **依从计算**：处方天数 × 每日次数 vs 实际记录次数，低于 80% 扣分。
3. **复诊间隔**：超过 90 天周期提示。
4. **缺数据**：最近 7 天一条没记，写「未记录」而不是猜。
5. **双重守卫**：数字可回查；「建议 / 诊断 / 可能是 / 考虑 / 疑似 / 推荐」出现即丢整行。

## 怎么用

```bash
pip install -e ".[dev]"
python -m chart seed
python -m chart summary --day 2026-11-27
python -m chart compose --day 2026-11-27
python -m chart serve        # http://127.0.0.1:8012
```

真实种子：12 条指标（血压高压、空腹血糖、糖化、TSH、体重等）、2 种药、2 次复诊。
`summary --day 2026-11-27` 报出 6 项：4 条指标越界（血糖 6.3 / 6.5、糖化 6.2、血压高压 141）、二甲双胍依从 66%、最近 7 天无记录，合计扣 23 分；复诊 50 天仍在 90 天周期内，不提示。

## 规则与扣分

| rule_id | 含义 | 扣分 |
| --- | --- | --- |
| `metric.out_of_range` | 指标超出参考区间 | 4 |
| `adherence.missed` | 依从率 < 80% | 5 |
| `visit.overdue` | 超过复诊周期 | 3 |
| `data.missing` | 最近 7 天无记录 | 2 |
| `guard.number` | 数字不在记录里，整行丢弃 | 8 |
| `guard.diagnosis` | 出现判断词，整行丢弃 | 10 |

## 边界

- 不做诊断、不给用药建议，导出物只陈述记录；
- 参考区间写在 `data/ranges.json`，按自己的化验单改；
- 数据只在本机 SQLite。

## 作者

shiyi · GitHub [@wushiyi105-jpg](https://github.com/wushiyi105-jpg) · wushiyi105@gmail.com
