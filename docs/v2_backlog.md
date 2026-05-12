# v2 backlog

> v1([`../BLUEPRINT.md`](../BLUEPRINT.md) 的 M1-M7)是项目的**及格线** —— 端到端、单源、ticker 聚合。下面三条是**满分线**,做完才能从"周期作业"变成有研究价值的反指系统。
>
> **硬约束:v1 不到 30 天稳定数据前,不要开 v2。** 没数据支撑的扩展全是空想。

---

## 1. 作者级反指建模(M3.5)

- **核心洞见:** ticker 聚合把信号拍平了。真正的"反指"价值在于识别**哪些个体 / 群体值得反着做**,而不是整体散户情绪。
- **改动:** ScoredPost 已经有 `post_id`,但没存 `author_id` 的累计画像 → 加 M3.5「作者维度聚合」,维护 `author_reliability` 表(每个 ID 的反指可靠度 = 历史看多/看空 vs 之后真实涨跌的相关性)。
- **关键文件(预想):** `src/aggregate/author.py` + SQLite `author_reliability` 表
- **依赖:** v1 至少跑满 60 天,有足够的 author × 时点样本

---

## 2. 多源 cross-check(M1 扩源)

- **核心洞见:** 单 XHS 结构性弱 —— memory `m1-field-findings` 实测:`机器人` keyword 50% 噪声,一条产品视频 1.4k 赞就把 sentiment 糊掉。
- **改动:** M1 加雪球(散户结构化讨论)/ 微博(广度)/ Google Trends(脱敏注意力代理)三源,**三源共升才算真"散户情绪"**,任一源单升降权。
- **关键文件(预想):** `src/scraper/{xueqiu.py, weibo.py, gtrends.py}` + RawPost 加 `source` 字段
- **依赖:** v1 单源 baseline 建立后才看得出多源 cross-check 的增量

---

## 3. 模型蒸馏(M4 加节,决定项目能否长跑)

- **核心洞见:** M4 横评不是为了选最贵的模型,**是为了拿 GPT-4o 答案当 ground truth,蒸馏到 Qwen2.5-7B 本地跑**。
- **成本视角:** $1/天/4 标的看着不贵,扩到 20 标的就是月 $150,半年项目会因成本放弃。蒸馏后砍 50-100x。
- **改动:** M4 增加一节 `distillation`:用 GPT-4o 在 5000 条无标注语料上打分 → LoRA 微调本地 Qwen2.5-7B → 在 labeled_200 上验证准确率不降太多(目标 ≤ 5%)。
- **关键文件(预想):** `src/eval/distill.py` + `models/qwen-7b-rednote-lora/`
- **依赖:** M4 已选出 teacher model

---

*最后更新:2026-05-13*
