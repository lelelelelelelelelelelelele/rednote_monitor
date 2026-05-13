# Claude Code 协作指导

> 这个 CLAUDE.md 会被 Claude Code 自动加载到 context。Claude 在本项目下帮 partner 干活时,**必须遵守下面的约束**。详细文档用 @-reference 列出,按需 Read。

---

## 一句话项目

多人协作的小红书反指系统,LLM 给散户帖子打情绪分,日度聚合作为"反指"信号。当前 **Week 1 M1 阶段**。完整设计 @BLUEPRINT.md。

---

## 必读三份文档

| 文档 | 什么时候 Read |
|---|---|
| @docs/collab_guide.md | partner 让你做任何 git / PR / merge 操作**前** |
| @.github/pull_request_template.md | partner 让你发 PR 时,描述**严格按 4 问填** |
| @BLUEPRINT.md | partner 提到 M1-M7 / 数据契约 / KPI / 模块分工时 |

---

## 硬约束(违反 = main 损坏 / 全员炸)

### 1. 永远不能直推 main

```powershell
# ❌ 永远不要这样
git push origin main

# ✅ 起 feature 分支
git checkout -b feat/m{X}-{短描述}
```

X = 模块编号(M1-M7,见 @BLUEPRINT.md § 二)。partner 没说改哪个模块时,**问清楚再动**。

### 2. 模块边界:不要越界改别人的代码

| 模块 | 目录 |
|---|---|
| M1 Scraper | `src/scraper/` |
| M2 Sentiment | `src/sentiment/` |
| M3 Aggregator | `src/aggregate/` |
| M4 Eval | `src/eval/` |
| M5 Backtest | `src/backtest/` |
| M6 Dashboard | `app/` |
| M7 Notify | `src/notify/` |

partner 要你改**不属于他模块**的代码 → **先提醒他可能越界**,让 user 确认后再动。

### 3. 4 个核心受保护文件 — 改之前先停下

下面任一文件被改 = 全员炸的风险。**partner 要你动这些,你必须先停下来回答他**:

> "这是核心受保护文件,本项目流程要求**群里 +1** + **Code Owner approve**(详见 collab_guide § 三)。确认要走流程吗?"

- `src/models.py` —— 数据契约(RawPost / ScoredPost / DailyMetric)
- `config/prompts.yaml` —— M2 LLM prompt
- `config/watchlist.yaml` —— ticker 清单
- `scripts/daily_run.py` —— 调度入口

详细流程:@docs/collab_guide.md § 三。

### 4. PR 描述必须按模板逐条填

发 PR 时(`gh pr create` 或网页),描述**严格按 @.github/pull_request_template.md 的 4 个问题填**,不要跳问,不要简化。partner 跑没跑过 happy path 你不知道就直接问他,**不要假设**。

---

## 工作流速查

```powershell
# 1. 同步 main
git checkout main && git pull

# 2. 起分支
git checkout -b feat/m2-first-happy-path

# 3. 干活...

# 4. commit(显式列文件,不要 git add -A)
git add src/sentiment/engine.py src/sentiment/prompts.py
git commit -m "M2: first happy path with GPT-4o-mini"

# 5. push 后去网页发 PR
git push -u origin feat/m2-first-happy-path
```

**长跑分支(>3 天)**每 2-3 天 `git rebase origin/main` 防漂移。

---

## v2 范围 — 不要现在做

@docs/v2_backlog.md 里三件事(作者级反指 / 多源 cross-check / 模型蒸馏)是 **v1 跑满 30 天之后**才做。partner 提出这些方向时,**先提醒他这是 v2 范围**,等 user 拍板再动手。

---

## 协作风格 hint

- 写代码默认中文注释 + 中文 commit message(已有 commit 都是中文)
- vibe-coding 项目,接口比内部实现重要;数据契约改前停下问 user
- 用 `uv` 管包,不用 pip
- Windows 主机,PowerShell 优先;命令尽量给 PowerShell 写法
