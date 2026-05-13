<!-- partner / LLM 请填完这 4 项,每项 1-2 行就够。不填的 PR 不要 merge。 -->

## 1. 改了什么
- 模块: <!-- e.g. M2 Sentiment Engine -->
- 主要文件: <!-- e.g. src/sentiment/engine.py + config/prompts.yaml -->
- 一句话目的: <!-- 比如:接 GPT-4o-mini 跑通 ScoredPost happy path -->

## 2. 跑过 happy path 没

- [ ] 已跑通,贴 1 行输出:

```
<!-- e.g. python scripts/daily_run.py --date 2026-05-13 → OK, 1 DailyMetric written -->
```

## 3. 是否动过核心受保护文件

下列任一被改 = 视为契约改动,必须群里 +1 + 走 CODEOWNERS cross-check:
- `src/models.py` —— 数据契约
- `config/prompts.yaml` —— LLM prompt
- `config/watchlist.yaml` —— ticker 清单
- `scripts/daily_run.py` —— 调度入口

- [ ] 没动上面任一文件
- [ ] 动了 → 已群里 +1(CODEOWNERS 会自动 @ 全员,需另 1 人 approve 才能 merge)

## 4. 是否动过 `pyproject.toml`

- [ ] 没动
- [ ] 加了依赖:<!-- 列包名 + 一句话原因 -->
