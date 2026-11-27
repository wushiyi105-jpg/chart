# 更新记录

## Unreleased

- `0001_init` 改为显式 `op.create_table` / `op.create_index`，运行期走 `alembic upgrade`
- `app/` 只依赖 `ports`，新增内存假实现用例
- 开 ruff `E2`/`E3`；CI 增加 `docker build` 与 `/health` 探活

## 1.0.0

- 8 个指标参考区间与越界标记
- 依从率计算（处方天数 × 每日次数）
- 复诊周期提示
- 最近 7 天缺数据写「未记录」
- 双重守卫：数字可回查、判断词整行丢弃
- CLI 与 Web 双入口
