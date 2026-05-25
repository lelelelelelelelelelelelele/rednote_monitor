# rednote_monitor

> 在小红书上抓散户讨论 → 多模态 LLM 打情绪分 → 日度聚合为「乐观度 / 讨论量」 → 辅助人工交易决策的**反指**信号。

设计、模块契约、KPI、风险全在 [`BLUEPRINT.md`](./BLUEPRINT.md)。本 README 只讲怎么跑起来。

---

## 当前状态(2026-05-13)

- 阶段:**Week 1 · M1 端到端打通**
- 唯一启用标的:`oracle`(甲骨文 / ORCL),其余三只在 `config/watchlist.yaml` 里 `enabled: false`
- 已落地:`src/scraper/{base,manual}.py` + `src/models.py` + 一条样本数据 `data/raw/2026-05-13_oracle.jsonl`
- 还没动:M2 Sentiment / M3 Aggregator / M4 Eval / M5 Backtest / M6 Dashboard / M7 Notify

详细里程碑见 BLUEPRINT § 五。

---

## 快速上手

### 0. 网络环境(中国大陆)

`git push` / `git clone` / `pip install` 等操作需要稳定访问 GitHub。如果连接超时,推荐用 [DevSidecar](https://github.com/docmirror/dev-sidecar) 一键加速,命令行操作也能受益。

### 1. 装依赖

```powershell
cd H:\project\rednote_monitor
uv sync
```

### 2. 起 xiaohongshu-mcp(M1 真 scraper 走它)

M1 的 scraper 依赖第三方 MCP:[xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)。

> **这个依赖不在本仓库里。** `external/` 整个被 `.gitignore` 了(含上游的二进制、cookies、自带的 .git),所以新 clone 的人**必须自己装**,装哪儿都行 —— 装到 `H:\project\rednote_monitor\external\xiaohongshu-mcp\` 可以零配置沿用本仓库的 `.mcp.json`。

安装、登录、跨平台部署一切以上游为准:

- 首选 → [上游 README](https://github.com/xpzouying/xiaohongshu-mcp#readme)
- macOS → 上游仓库里的 `deploy/macos/readme.md`(Linux / Windows 上游暂时没给专门的 deploy 文档)

启好后,本仓库 [`.mcp.json`](./.mcp.json) 已把 `http://127.0.0.1:18060/mcp` 注册给 Claude Code —— 进项目跑 `/mcp` 看到 `xiaohongshu: connected` 即可。

> 完整换机流程见 BLUEPRINT § 九.4。

### 3. 跑一条数据

M1 的 ManualScraper 兜底路径:把手抓的 30 条评论丢到 `data/raw/manual/{date}_{keyword}.txt`,然后跑 daily_run(待 M2/M3 接好后)。

目前真 scraper 已有 oracle 一条样本输出在 `data/raw/2026-05-13_oracle.jsonl`,可以直接喂给 M2(待实现)。

---

## 目录速查

```
.
├── BLUEPRINT.md           # 设计文档,主要看这个
├── config/watchlist.yaml  # 标的 + 关键词
├── src/                   # 业务代码(scraper / sentiment / aggregate / ...)
├── data/                  # 抓回来的 raw / scored,全部 gitignore
├── docs/architecture/     # 架构图三件套:schema.yaml(真值) + diagram.{mmd,png}
├── external/              # xiaohongshu-mcp + xhs-aigc-dataset,不入 git
└── .mcp.json              # Claude Code 的 MCP 配置
```

---

## 关键约定(踩过坑后总结的)

- **`src/models.py` 改字段前群里 +1**,所有模块都依赖它。
- **`data/raw/` 不入 git**(含真实用户昵称 / IP)。要分享样本数据,脱敏后放 `tests/fixtures/`。
- **`external/` 不入 git**,xiaohongshu-mcp 的 cookies 也不能 commit。
- **关键词字面歧义**:`甲骨文` 会召回古文字学习,`机器人` 会召回亲子手工。M2 必须输出 `is_relevant`,M3 聚合时按这个过滤(见 BLUEPRINT § 三)。
- **不传 `publish_time` 给 scraper**,只传 `sort_by=最新`;时间窗在客户端用 `int(post_id[:8], 16)` 反解切片。

---
