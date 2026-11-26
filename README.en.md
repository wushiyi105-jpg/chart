# Chart

[![test](https://github.com/wushiyi105-jpg/chart/workflows/test/badge.svg)](https://github.com/wushiyi105-jpg/chart/actions)

![usage](assets/demo.gif)

Three months of metrics, meds and visits compressed into one page for a doctor.

## What it does

- aggregates 8 chronic metrics and flags out-of-range values;
- computes adherence from prescription days and logged doses;
- reminds when the follow-up interval is exceeded;
- writes "not recorded" instead of guessing;
- two guards: numbers must be traceable, any diagnostic wording drops the line.

## Run

```bash
pip install -e ".[dev]"
python -m chart seed
python -m chart summary --day 2026-11-27
python -m chart serve
```

## Author

shiyi · GitHub [@wushiyi105-jpg](https://github.com/wushiyi105-jpg) · wushiyi105@gmail.com
