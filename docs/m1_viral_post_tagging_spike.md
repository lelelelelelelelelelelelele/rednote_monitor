# M1 改进 spike:爆款帖评论 ticker tagging

> 写于 2026-05-27 凌晨。lele 设计、待执行。30 min spike → 决定 M1 走向。
> 关联讨论:跟 Claude session 2026-05-26 那段对话。

---

## TL;DR

现在 M1 按 ticker keyword 搜帖,问题是噪声大(`甲骨文` 50% 是古文字)、低频 ticker 0 数据。

**假设**:换个源头—— 不按 ticker 搜,而是抓**爆款情绪股票帖**,从评论里逐条抽 ticker mention,可能信号密度更高、噪声更低。

**Spike 目的**:验证爆款帖评论里能明确归到 ticker 的比例**≥ 20%** 才值得大改 M1。

---

## 一、核心假设(要被验证的)

> 一个 XHS 真实爆款股票帖(n_likes ≥ 1000)的 ≈ 500 条评论里,
> **能明确归到某个 ticker / 板块的评论占比 ≥ 20%。**

为啥 20% 是阈值:
- < 5% → 没数据,这条路废
- 5%-20% → 信号有但稀,不如老路效率高
- ≥ 20% → **每帖能产 100+ 条 ticker-tagged 评论**,远超 per-ticker 搜出来的 30 评论/帖

---

## 二、Spike 步骤(预计 30 min,手动 + 半自动)

### Step 1 · 手动找 2-3 个爆款情绪帖(5 min)

打开 XHS app/网页,搜 "炒股 / 牛市 / 抄底 / 大盘 / A股 / 美股":
- 选 n_likes ≥ 1000 的
- 内容明显**情绪化**(短、感叹号多、晒持仓 / 哭诉 / 梭哈),**不是**机构研报转载、不是硬核分析
- 选 2-3 个,记 post URL 和 post_id

候选关键词清单(meta-keyword,跟 ticker 无关):
```
炒股 / A股 / 港股 / 美股 / 大盘 / 牛市 / 熊市 / 抄底 / 梭哈 /
被套 / 割肉 / 财报季 / 股市 / 股票 / 持仓 / 跑路 / 反弹
```

### Step 2 · 用 xhs-mcp 拉评论(10 min)

参考之前 manual 拉数据的做法,把这 2-3 帖的 detail.json(含全部评论)落到 `data/raw/manual/spike_viral_*` 目录。

注意拉 **全量评论**(不只是前 30 条),爆款帖评论才是核心数据。

### Step 3 · 用 M2 改 prompt 跑 ticker tagging(10 min)

借 lush0622 现有的 `SentimentEngine`,临时改 prompt:

原 prompt(评论 batch):
```
对每条评论返回 {comment_id, sentiment(-2..+2), is_relevant}
```

改成:
```
对每条评论返回 {
  comment_id,
  sentiment(-2..+2),
  is_relevant(本评论是否在表达对某只股票/板块的看法),
  ticker(若有提及,canonical 形式:NVDA/ORCL/HSTECH/A50/SOX/比特币/...;无则 null)
}
```

跑这 2-3 帖的所有评论,落盘 JSONL,看产出。

### Step 4 · 统计 + 决策(5 min)

```python
n_total_comments = 2-3 帖评论数总和
n_with_ticker = ticker is not null 的评论数
hit_rate = n_with_ticker / n_total_comments

if hit_rate >= 0.20:
    print("GO → 大改 M1,走 comment-tagging 路线")
elif hit_rate >= 0.05:
    print("WAIT → 信号弱,先 v1.5 多层过滤,作为并行补充流再说")
else:
    print("NOGO → 假设不成立,回去走 v1.5 多层过滤")
```

也看一眼分布:**ticker 集中度**。如果 80% 的命中都是 "NVDA" 一只票,实际可观测的 ticker 还是少;最好至少能覆盖 5+ ticker。

---

## 三、若 GO:M1 v2 大改 outline

### 数据契约改动(走 CODEOWNERS cross-check)

- `RawPost.keyword`:重命名/扩展。改成 `recall_keyword`(召回用的 meta-keyword),不再是 ticker
- `RawPost.recall_strategy`:加一个枚举 `["ticker_search", "viral_emotional_post"]` 标记来源
- `CommentScore` 加 `ticker: str | None` 字段
- `DailyMetric` 聚合逻辑改:按 evidence 来源 ticker 而不是 post.keyword 切桶
- `config/watchlist.yaml` schema 改:除了 per-ticker 配置,加一段 meta-keyword 池

### 新 M1 双源工作流

```
源 A · 爆款情绪帖 (主线,数据密度高)
  meta-keyword 搜 → 互动门槛过滤 → 情绪文风过滤 →
  全量拉评论 → M2 逐条 sentiment+ticker tagging →
  按 ticker 切桶聚合

源 B · per-ticker keyword 搜帖 (兜底,低频 ticker)
  原 v1 流程保留,但只跑源 A 覆盖不到的 ticker
```

### KPI 改动

BLUEPRINT M1 KPI "每天产 ≥ 40 条相关 RawPost" 改成:
**"每个 active ticker 每天产 ≥ 20 条 ticker-tagged 评论"**(单位从 post 变 tagged-comment)

---

## 四、若 NOGO:退回 v1.5 多层过滤

回到 2026-05-26 那次讨论的 5 层过滤设计(召回 → 客户端硬过滤 → 作者元数据过滤 → M2 is_relevant → KPI 监控)。

watchlist.yaml schema 改造:
```yaml
- id: oracle
  keywords_include: [...]
  keywords_exclude: [...]   # 负词排除
  min_likes: 10
  min_comments: 3
  min_text_chars: 30
```

---

## 五、风险/未知

1. **爆款帖 XHS 算法是否对自动化采集更敏感** —— BLUEPRINT § 八 风险 6 已 flag xhs-mcp 风控升级,爆款帖访问量大可能更受关注。先手动拉验证,不要程序化批量
2. **prompt 改动影响现有评测** —— labeled_200.csv 现在不带 ticker label,M4 评测覆盖不到新 prompt,需要重新标 ≥ 50 条带 ticker 的子集
3. **ticker 字典维护成本** —— "恒生科技 / HSTECH / 0700.HK / 腾讯" 这种 alias 映射要持续维护;前期靠 LLM 抽,后期可能要建本地词典加速
4. **partner 协同** —— prompt 改 + `src/models.py` 改 + `config/watchlist.yaml` 改都是 CODEOWNERS cross-check 范围,要群里 +1 lush0622 一起对齐

---

## 六、明早开干 checklist

- [ ] 找 2-3 个爆款情绪帖,记 URL/post_id
- [ ] xhs-mcp 拉全量评论,落 `data/raw/manual/spike_viral_*_detail.json`
- [ ] 临时改 prompt 跑 ticker tagging(或先抄一份 engine.py 改 prompt 不动主线代码)
- [ ] 算 hit_rate,看 ticker 分布
- [ ] 决策:GO / WAIT / NOGO,记结论到本文件 § 七
- [ ] 群里同步 lush0622(尤其 GO 的话要协同改 prompt + models)

## 七、供给侧策略矩阵 — "去哪里找这些情绪化讨论帖"

> 2026-05-27 深夜补:既然帖子可遇不可求,本节穷举所有"稳定拿到讨论密集帖"的方法,
> 按可行性 + 风险排序。明早 spike 前选 1-2 个去试。

### 选项 1 · 真爆款帖(被动等)
- 标准:n_likes ≥ 1000 的单帖爆款
- **优点**:质量最高,500+ 评论真实散户
- **缺点**:**可遇不可求**,整周可能 0 帖,supply 完全不可控
- **不推荐作为主线**,作为偶然 bonus 可

### 选项 2 · KOL 中等热度帖(关注列表)
- 标准:手动选 5-10 个股票垂直 KOL,全量拉他们最近 7 天的帖
- **优点**:每天稳定 3-5 帖,evergreen,KOL 圈子小好选
- **缺点**:需要手动维护关注列表;KOL 选偏会带 sample bias
- **可行性高**,推荐作为主线

### 选项 3 · 模板帖关键词搜(标题特征)⭐
> lele 提的"更好的方案",细化后:
- 标准:标题/正文符合"求讨论"句式的帖,**自然吸引情绪评论**:
  ```
  "怎么看 XX"  "如何看 XX"  "XX 还能上车吗"
  "XX 该不该买"  "XX 值不值得抄底"  "XX 能不能拿"
  "求大佬指点 XX"  "XX 还有救吗"  "XX 还能不能看"
  ```
- **优点**:
  - 模板帖**天然区分于硬核分析贴**(分析贴是结论,模板贴是问题)
  - 标题特征明显,可以用前缀/正则匹配,不用 LLM 分类
  - 全网海量,每天有,supply 稳定
  - 评论密度高:有人问就一定有人答
- **缺点**:模板帖可能本身互动一般(不是爆款),需要测一下 KOL 关注 + 模板搜 哪个评论密度高
- **强烈推荐作为主线**

### 选项 4 · DIY 自发帖(取巧版)⚠️
> lele 提的"最原始方案":自己每天发"怎么看 XXX",收完评论删帖,第二天换 ticker。
- **优点**:
  - 100% supply 可控,每天稳定有数据
  - 可以精准 cover watchlist 里每个 ticker
  - 评论自带 ticker 上下文(不用再 tagging)
- **缺点 / 风险**:
  - ❌ **XHS 反作弊高风险**:"发-收-删-再发" 是非常显眼的自动化模式,
    比单纯浏览采集更易被风控盯上(BLUEPRINT § 八 风险 6 已 flag)
  - ❌ **账号被封风险**:发布权限比读权限敏感得多,搞挂账号 = 同时挂掉 ManualScraper 兜底数据源
  - ❌ **Cold start**:新号发帖曝光低,可能 0 评论
  - ❌ **Sample bias**:来评论你帖的人是 self-select 受众(粉丝 / 算法推送对象),
    不代表全网散户分布;且容易被 MCN 水军盯上做"标记目标"
  - ❌ **持续操作负担**:即使脚本化,日常运维繁琐,与项目"vibe coding 低运维"调性不符
  - ❌ **合规边缘**:为数据采集目的批量发帖删帖,在 XHS 服务协议边缘,商用更敏感
- **结论**:**仅作 fallback 应急方案 记录,不作为主线**。
  哪天选项 2+3 都试过都不行,再考虑;且需要用副号、低频(每周 1-2 次)、不删帖。

### 推荐组合:**选项 3 主 + 选项 2 辅**

- 主线:模板帖关键词搜(选项 3),覆盖大盘 + 板块讨论
- 补充:5-10 个 KOL 关注列表(选项 2),作为"低 ticker mention 兜底"
- 备份:偶遇爆款(选项 1)作为 bonus,不作为主依赖
- 储备:自发帖(选项 4)只在前三个都失败时启用,且全员讨论过风险后

---

## 八、Spike 结论(明早填)

- 拉了几帖:
- 总评论数:
- ticker 命中:
- hit_rate:
- ticker 分布(top 5):
- 决策:
- 下一步:
