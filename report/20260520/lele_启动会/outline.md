# rednote_monitor 项目启动会

> 生成日期：2026-05-20
> 生成方式：AI-assisted (Claude Code + pptxgenjs)

---

## 第 1 页 | 封面

**标题：** rednote_monitor 项目启动会
**副标题：** 小红书散户情绪反指系统
**底部：** 2026.05.20 | LSM · QBW · LELE

**设计：** 深色背景（Midnight Executive: navy #1E2761），左侧装饰圆，冰蓝副标题

---

## 第 2 页 | 项目简介

**我们在做什么**

> 对小红书上指定 ticker 的相关帖子进行多模态情绪打分，日度聚合输出"乐观/悲观"和"讨论量"两个指标，辅助人工交易决策。

**三列要点：**
- 输出什么：DailyMetric（SQLite 日度指标表）
- 怎么实现：LLM 多模态打分 → 日度聚合 → 回测验证 → Dashboard 可视化
- 现在到哪了：Week 1 M1（端到端骨架打通）

---

## 第 3 页 | 🤖 AI 友好声明

**这是一个 vibe-coding 项目 · AI 是一等公民**

**三张卡片：**

| 卡片 | 一句话 |
|---|---|
| AI 写代码 | commit / PR / issue 都行，标好 Co-Authored-By 就 OK，不用刻意"伪装人写的" |
| AI Assistant 工具链 | cc / Cursor / Codex / ChatGPT 任选；`BLUEPRINT.md` + `CLAUDE.md` 是给 AI 看的真值文档，改这两份等于给所有人的 AI 同步 |
| 协作的边界 | 写代码很自由；改 4 个核心受保护文件走 PR 大家看一下；架构方向最终人拍板，AI 是助手不是 owner |

**为啥强调这点：** 团队规模小、节奏快、同学开发经验深浅不一 —— AI 把门槛拉平，让大家把精力放在判断和设计上，不在语法和样板代码上。

---

## 第 4 页 | 系统架构总览

**引用 docs/architecture/diagram.png（非线性架构图）**

**7 个模块：**
M1 Scraper | M2 Sentiment | M3 Aggregator | M4 Eval | M5 Backtest | M6 Dashboard | M7 Notify

**关键约束：** 模块间只走 JSON / SQLite，不互相 import

**数据流：**
- M1 → data/raw/*.jsonl → M2 → data/scored/*.jsonl → M3 → SQLite daily_metrics
- M4 读 labeled_200.csv 评测
- M5 读 SQLite + yfinance 回测
- M6/M7 消费 SQLite

---

## 第 5 页 | 团队分工

**模块归属（M6 + M7 Week 2 再分）**

| 负责人 | 模块 | 核心交付 |
|--------|------|----------|
| LSM | M2 + M3 + M4 | 打分质量闭环：prompt → 聚合 → 评测 |
| LELE | M1（暂时） | 每日 ≥40 条 RawPost，ManualScraper 兜底 |
| QBW | M5 Backtest | 90 天 IC + 事件研究 |
| 待定 | M6 + M7 | Dashboard + Notify（Week 2 末再分） |

---

## 第 6 页 | 关键设计决策

**模块能并行的两条腿：端口解耦 + 协议确定**

**左：端口解耦**
- 模块间只走 JSON 文件 / SQLite，不互相 import
- 接口冻结后，内部实现怎么改都不影响别人
- 7 个模块的并行排期，靠这个前提撑起来

**右：协议确定（数据契约）**
- RawPost（M1 → M2）
- ScoredPost（M2 → M3）
- DailyMetric（M3 → SQLite）
- 红线 4 文件改前群里 +1：
  src/models.py / config/prompts.yaml / watchlist.yaml / scripts/daily_run.py

**底部三条非显然约定：**
- post / comment 分开打分（XHS 上常常情绪相反）
- M2 必须输出 `is_relevant` 门控（宽 keyword 噪声实测 ~50%）
- 反讽子集 ≥70% 才上线（M4 兜底）

---

## 第 7 页 | 协作流程

**怎么不炸**

```powershell
git checkout main && git pull
git checkout -b feat/m2-sentiment
# ...写代码...
git add src/sentiment/engine.py
git commit -m "M2: first happy path"
git push -u origin feat/m2-sentiment
# PR 网页发，按模板 4 问填
```

**硬约束：**
1. 永远不直推 main
2. 核心文件改前群里 +1
3. 模块边界不越界
4. PR 描述按模板 4 问

---

## 第 8 页 | 周演示 · 欢迎角度

**这几点都欢迎聊，自由发挥，没卡到的角度跳过没事**

| 序号 | 板块 | 一句话 |
|---|---|---|
| 1 | 📐 架构图 | 自己模块的子架构 · 本周演化 |
| 2 | 🚀 进展 | 对应模块讲，量化结果 |
| 3 | ✅ To-do | 挂钩模块块 + 遇到的卡点 |
| 4 | 📊 Token 用量 | ccusage 数据，看大家烧在哪儿 |
| 5 | ❓ Q&A | 具体卡点 1-2 个就好 |

**为什么列这五个角度：** 架构 → 进展 → 计划 → 烧在哪 → 卡点，从宏观到细节顺一遍。讲多讲少看心情，vibe-coding 项目不打卡。

---

## 第 9 页 | 📐 架构图

**目的：** 讲自己模块的**子架构图**（不是顶层 BLUEPRINT），让大家看到你这块怎么搭、本周怎么演化

**怎么讲：**
- 架构是分层的：顶层 BLUEPRINT 一张总图 + 每个模块自己一张 sub-diagram
- 重点讲本周这张子图变了哪里、为什么变
- 顶层 BLUEPRINT 有人动了再单独提，不用每周复述

**话术示例：**
> 我这周 M2 内部把 sentiment engine 拆成了 prompt-builder + llm-caller + parser 三块，目的是把 prompt 调优和 LLM 调用解耦 —— 下周横评不同模型时 prompt-builder 这部分不用动。

---

## 第 10 页 | 🚀 进展

**目的：** 展示产出，同步状态

**怎么讲：**
- 对应架构图的模块来讲
- 格式：[模块名] 完成了什么 + 结果如何

**话术示例：**
> M1 采集模块：本周完成了对小红书新接口的适配，抓取成功率从 80% 提升到了 98%。

---

## 第 11 页 | ✅ To-do

**目的：** 同步下周计划，挂钩到模块块 + 本周遇到的卡点

**怎么讲：**
- 挂到具体模块（M1-M7），讲想推进到哪一步
- 顺带说一下踩到了啥卡点 / 担心啥 / 想怎么绕
- 不用列 Token 预算 —— token 是共享池，不抢不排名

**话术示例：**
> 下周继续推 M2 sentiment engine，想把 prompt 在反讽子集上准确率从 65% 提到 75%。担心的是 GPT-4o-mini 对反讽可能就这天花板了，如果不行就上 Sonnet 横评对比。

---

## 第 12 页 | 📊 Token 用量

**目的：** token 花费 ≈ 这周投入的粗略指标 —— 看大家精力砸在哪个模块、哪个任务上

**怎么讲：**
- 数据来源：ccusage
- 自己烧得多 / 少在哪个模块、哪个任务上，有没有意外发现
- 注意：token 反映**投入**不等于**产出**（试错、重跑也烧），但作为"这周做了多少事"的粗看够用

**话术示例：**
> 本周 M2 prompt 调优跑了好几轮，大概 120k；意外发现 vision 调用单价比纯文本贵 3x，下次准备先在文本-only 上 iterate 收敛了再上图。

---

## 第 13 页 | ❓ Q&A

**目的：** 解决卡点。**只针对本周遇到的实际问题讨论**，不做开放式建议征询、不发散

**怎么讲：**
- 提前准备 1-2 个具体卡住的问题
- 描述清楚：已经尝试过什么、卡在哪、自己的备选方案
- 没卡点直接跳过，比硬凑话题好

**话术示例：**
> 本周 M2 跑评论打分时，LLM 偶尔返回非 JSON 字符串，目前是 try/except 兜底，命中率约 3%。想问一下大家有没有更稳的 prompt 收敛方法。
