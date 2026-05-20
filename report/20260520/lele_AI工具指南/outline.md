# AI 工具使用指南

> 生成日期：2026-05-20
> 面向：3 人团队，AI 零基础
> 目的：分享好用的 AI 工具经验，降低使用门槛

---

## 第 1 页 | 封面

**标题：** AI 工具使用指南
**副标题：** Git · CC Usage · PPT 技能分享
**底部：** 2026.05.20

---

## 第 2 页 | 为什么写这份指南

**团队现状**
- 3 人协作，项目节奏快
- 部分同学较少接触 AI 工具
- 用好工具 = 把时间花在判断和设计上，不在重复劳动上

**三个核心场景**
1. Git — 代码协作不炸
2. CC Usage — 花明白钱，知道 Token 烧在哪
3. AI 做 PPT — 汇报材料快速产出

---

## 第 3 页 | Git 极简工作流（1/3）为什么必须学

**没有版本控制的痛**
- 文件叫 `final_v2_真的final_不改了.docx`
- 谁改了哪行、为什么改，完全找不到
- 三个人同时改，覆盖来覆盖去

**Git 解决什么**
- 时光机：任何时候回到之前的版本
- 协作：三个人并行改，最后自动合并
- 问责：每行代码谁写的、什么时候写的，清清楚楚

---

## 第 4 页 | Git 极简工作流（2/3）5 个够用命令

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

## 第 5 页 | Git 极简工作流（3/3）分支规则和常见坑

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
- 用 Claude Code 的 `pptx` skill 直接生成 .pptx
- 或用在线工具（Gamma、Tome）导入 Markdown

**Step 4：人工润色**
- AI 生成的是骨架，数据必须自己核对
- 关键结论和数字，人工 double-check
- 配色和字体按公司规范调整

---

## 第 10 页 | 快速上手清单

**这周就能用起来的 3 件事**

1. **Git**：把当前项目 init 了，每天下班前 commit 一次
2. **CC Usage**：装完跑 `ccusage today`，建立 baseline
3. **PPT**：下次汇报前，先用 AI 生成大纲，再自己填内容

**进阶路线**
- Week 1：熟练 Git 基础循环
- Week 2：看懂 CC Usage 报告，优化 token 消耗
- Week 3：独立用 AI 完成一页 PPT 从大纲到成品

---

## 第 11 页 | 结束页

**标题：** 开始用吧
**副标题：** 工欲善其事，必先利其器
**底部：** 有问题随时问
