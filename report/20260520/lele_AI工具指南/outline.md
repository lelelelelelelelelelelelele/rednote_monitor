# AI 工具使用指南

> 生成日期：2026-05-20
> 面向：3 人团队，AI 零基础
> 目的：分享好用的 AI 工具经验，降低使用门槛

---

## 第 1 页 | 封面

**标题：** AI 工具使用指南
**副标题：** 让团队少烧时间，多攒判断
**底部：** 2026.05.20

---

## 第 2 页 | 这份指南讲什么

**一句话**
工具用对了，时间就花在判断和设计上，不在重复劳动上。

**6 张卡片速览（2×3 网格）**

| 卡片 | 主题 | 一句话 |
|---|---|---|
| 1 | Git 工作流 | 命令集 + 分支规则 + PR |
| 2 | DevSidecar | GitHub timeout？一键加速 |
| 3 | GitHub PR 扩展 | VSCode 里直接 review PR |
| 4 | CC Usage | 知道 Token 烧在哪 |
| 5 | pptx skill | 让 AI 写 PPT 代码 |
| 6 | AI 提示词速查 | 给 Claude Code 的真实工作流 |

---

## 第 3 页 | Git 极简工作流（1/4）为什么必须学

**没有版本控制的痛**
- 文件叫 `final_v2_真的final_不改了.docx`
- 谁改了哪行、为什么改，完全找不到
- 三个人同时改，覆盖来覆盖去

**Git 解决什么**
- 时光机：任何时候回到之前的版本
- 协作：三个人并行改，最后自动合并
- 问责：每行代码谁写的、什么时候写的，清清楚楚

---

## 第 4 页 | Git 极简工作流（2/4）5 个够用命令

```powershell
# 1. 克隆项目（第一次）
git clone https://github.com/xxx/xxx.git

# 2. 拉最新代码（每次开干前）
git pull

# 3. 看改了什么
git status

# 4. 提交改动（三步：add → commit → push）
git add 文件名
git commit -m "描述你改了什么"
git push

# 5. 起分支（重要！不要直接推 main）
git checkout -b feat/功能名
```

**记不住？只记这张图：**
`pull` → 改代码 → `add` → `commit` → `push`

---

## 第 5 页 | Git 极简工作流（3/4）分支规则和常见坑

**分支命名**
- `feat/新功能` — 新功能
- `fix/bug描述` — 修 bug
- `docs/文档更新` — 改文档

**黄金规则**
1. 永远不直推 main
2. 每次开干前先 `git pull`
3. 改动相关文件一起 commit，不要攒一大堆再提交
4. push 不上？先 pull 再 push

**常见坑**
| 现象 | 原因 | 解决 |
|------|------|------|
| push 被拒 | main 有更新 | 先 pull，再 push |
| 冲突了 | 两个人改了同一行 | 手动选要哪边，再 commit |
| 忘了起分支 | 直接改了 main | `git stash` 暂存 → 起分支 → `git stash pop` |

---

## 第 5.4 页 | Git 极简工作流（4/4）Pull Request 工作流

**为什么不能直推 main**
- 改坏全员炸（尤其本项目的 4 个核心受保护文件）
- PR = 一次 review 机会 + 完整改动留痕

**两种发法**

A. 网页（推荐新手）
1. push 完去 GitHub 首页
2. 黄色横条 "Compare & pull request"
3. 描述框**自动加载** `.github/pull_request_template.md`
4. 填完 4 个问题 → Create → Merge

B. 命令行（`gh` CLI，更快）
```bash
gh pr create        # 自动用模板
gh pr view --web    # 浏览器打开
gh pr merge --squash
```

**本项目 PR 模板的 4 个问题**
1. 改了什么（模块 + 文件 + 一句话目的）
2. 跑过 happy path 没（贴 1 行输出）
3. 是否动过 4 个核心受保护文件
4. 是否动过 `pyproject.toml`

**红线**：改 `src/models.py` / `config/prompts.yaml` / `config/watchlist.yaml` / `scripts/daily_run.py` → 必须群里 +1，CODEOWNERS 自动 @，强制 cross-check

---

## 第 5.5 页 | 实用工具推荐：DevSidecar

**问题**：`git push` / `git clone` 连不上 GitHub，报错 timeout
**解决**：[DevSidecar](https://github.com/docmirror/dev-sidecar) — 开发者边车，一键加速

**特点**
- 桌面软件，Windows / Mac / Linux 都支持
- 点击"一键加速"，系统全局生效
- 命令行里的 `git push` 也能走加速通道
- 同时还加速 npm、pip、Stack Overflow 等开发平台

**适用场景**
- 日常 `git clone` 大型仓库
- `pip install` / `npm install` 装依赖
- 访问 GitHub Release 下载文件

---

## 第 5.6 页 | 实用工具推荐：GitHub Pull Requests

**问题**：网页 GitHub 看 PR、写评论、来回切换浏览器和编辑器，效率低
**解决**：[GitHub Pull Requests](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-pull-request-github) — VSCode 官方扩展（微软 / GitHub 出品）

**特点**
- VSCode 扩展，装完侧边栏直接看 PR / Issue 列表
- 在编辑器里 review 代码、写行内评论、resolve conversation
- 一键 checkout 别人的 PR 分支到本地，调完直接 push
- 别人对你 PR 的评论实时弹通知，不用守着网页

**适用场景**
- 日常 review 同事的 PR
- 自己起 PR 时填模板（自动识别 `.github/pull_request_template.md`）
- 处理 review comments，不用在网页和 VSCode 之间来回跳

---

## 第 6 页 | CC Usage（1/2）Token 是什么，为什么要统计

**Token = AI 模型的计费单位**
- 不是字数，是模型处理文本时的最小单元
- 英文大约 1 token ≈ 0.75 个单词
- 中文大约 1 token ≈ 0.5 个汉字
- 输入和输出都计费

**为什么要监控**
- LLM 调用按 token 计费，烧多了直接体现在账单上
- 知道钱花在哪 = 知道时间花在哪
- 发现异常消耗（比如死循环调用、重复请求）

---

## 第 7 页 | CC Usage（2/2）用法和省钱技巧

**安装**
```powershell
npm install -g ccusage
# 或
pip install ccusage
```

**常用命令**
```powershell
ccusage today          # 今天用了多少
ccusage week           # 本周统计
ccusage by-model       # 按模型分（GPT-4o / Claude / 等）
ccusage by-project     # 按项目分
ccusage export --csv   # 导出报表
```

**省钱实操**
1. 开发期用便宜模型（GPT-4o-mini），调好了再上贵的
2. 给 AI 的上下文只放必要的，历史对话太长会累积计费
3. 批量处理比单条循环省 token
4. 定期 `ccusage week` 看一眼，异常消耗早发现

---

## 第 8 页 | AI 辅助做 PPT（1/2）工作流

**传统做法 vs AI 做法**

| 步骤 | 传统 | AI 辅助 |
|------|------|---------|
| 写大纲 | 自己想 | 告诉 AI 主题和目标受众，生成大纲 |
| 写内容 | 逐页敲 | AI 按大纲扩写每页要点 |
| 排版 | 手动调 | Markdown / 文本 → 自动生成 PPT |
| 美化 | 找模板 | AI 建议配色、配图 |

**核心公式**
> 给 AI 的指令 = 主题 + 受众 + 页数 + 风格 + 特殊要求

---

## 第 9 页 | AI 辅助做 PPT（2/2）实操步骤

**Step 1：生成大纲**
```
请帮我做一个 PPT 大纲：
- 主题：Q2 季度复盘
- 受众：部门总监
- 页数：10 页左右
- 风格：数据驱动，突出成果
```

**Step 2：扩写内容**
把大纲的每页丢给 AI，要求扩写成 bullet points。

**Step 3：生成 PPT 文件**
- 用 Claude Code 的 `pptx` skill 直接生成 .pptx（推荐，下页详讲）
- 或用在线工具（Gamma、Tome）导入 Markdown

**Step 4：人工润色**
- AI 生成的是骨架，数据必须自己核对
- 关键结论和数字，人工 double-check
- 配色和字体按公司规范调整

---

## 第 9.5 页 | 重点：Claude Code 的 pptx skill

> **Meta：你现在看的这份 PPT，就是 pptx skill 生成的。**

**怎么触发**
- Claude Code 里直接说「帮我做一份 XX 主题的 PPT」
- 或显式调用 `/pptx`，skill 会自动加载

**工作流（4 步全自动）**
1. 你给 **outline.md**（文字大纲，自己写或让 AI 先写）
2. Claude 写 **gen.js**（用 pptxgenjs 库，代码即 PPT）
3. `node gen.js` 输出 **.pptx**
4. PowerShell 一键转 **.pdf** 给没装 Office 的人看

**和 Gamma / Tome 比的优势**
| 维度 | Gamma / Tome | pptx skill |
|---|---|---|
| 输出 | 在线网页 | 标准 .pptx 文件 |
| 改稿 | 网页编辑器 | 改 outline.md 或 gen.js，可 diff |
| 版本控制 | 无 | git 管起来 |
| 风格自定义 | 选模板 | 任意配色/字体/版式 |
| 离线分享 | 导出有水印 | 原生 .pptx + .pdf |

**适合什么场景**
- 团队周报、技术分享（需要 git 留痕、多人改）
- 风格统一的系列汇报（gen.js 可复用模板）
- 不适合：一次性、追求酷炫动效的演示（用 Gamma 更快）

---

## 第 9.7 页 | AI 提示词速查（结合本项目 CLAUDE.md）

> **前提**：项目根有 `CLAUDE.md`，Claude Code 会自动加载，不用每次重复项目背景。

**① 起分支 + 干活**
```
我要开始做 M2 sentiment engine。
按 CLAUDE.md 的规范起分支，
然后实现 src/sentiment/engine.py 的 happy path。
```

**② 写 commit message**
```
看一下 git status 和 git diff，
按本项目风格（中文、模块前缀如 "M2:"、简洁）
帮我写 commit message。
```

**③ 发 PR**
```
git diff main 看一下，
按 .github/pull_request_template.md 的 4 个问题
帮我生成完整 PR 描述。
Happy path 我跑过了，输出："OK, 1 DailyMetric written"
```

**④ Review diff（自查或互查）**
```
review 这个 PR 的 diff，重点检查：
- 是否越界改了别人模块的代码（M1-M7 分工见 BLUEPRINT § 二）
- 是否动了 4 个核心受保护文件
- 接口和 BLUEPRINT § 三的数据契约对得上吗
```

**关键点**：这些提示词都不用重复"项目是干啥的""模块怎么分"——Claude Code 自动读 CLAUDE.md / BLUEPRINT.md / PR 模板。

---

## 第 10 页 | 快速上手清单

**这周就能用起来的 3 件事**

1. **Git**：把当前项目 init 了，每天下班前 commit 一次
2. **CC Usage**：装完跑 `ccusage today`，建立 baseline
3. **pptx skill**：下次汇报前，让 Claude Code 给你出一版

**碰到具体问题装这两个**
- GitHub timeout / 慢 → DevSidecar
- 总在网页和编辑器之间切来切去看 PR → GitHub Pull Requests 扩展

**进阶路线**
- Week 1：熟练 Git 基础循环 + 装好两个辅助工具
- Week 2：看懂 CC Usage 报告，优化 token 消耗
- Week 3：用 pptx skill 完成一份完整汇报（outline → gen.js → pdf）

---

## 第 11 页 | 结束页

**标题：** 开始用吧
**副标题：** 工欲善其事，必先利其器
**底部：** 有问题随时问
