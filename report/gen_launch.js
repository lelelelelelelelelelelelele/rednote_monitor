const pptxgen = require("pptxgenjs");

// ============================================
// 配色: Midnight Executive
// ============================================
const NAVY     = "1E2761";
const ICE_BLUE = "CADCFC";
const WHITE    = "FFFFFF";
const SLATE    = "64748B";
const LIGHT_BG = "F8FAFC";

function makeShadow() {
  return { type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.12 };
}

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "LELE";
pres.title = "rednote_monitor 项目启动会";

// ============================================
// 第 1 页 | 封面 (深色底)
// ============================================
let s1 = pres.addSlide();
s1.background = { color: NAVY };

// 装饰圆
s1.addShape(pres.shapes.OVAL, {
  x: 7.5, y: -1.5, w: 4, h: 4,
  fill: { color: ICE_BLUE, transparency: 85 }
});
s1.addShape(pres.shapes.OVAL, {
  x: -1.2, y: 3.8, w: 2.5, h: 2.5,
  fill: { color: ICE_BLUE, transparency: 90 }
});

// 主标题
s1.addText("rednote_monitor", {
  x: 0.8, y: 1.6, w: 8.4, h: 0.9,
  fontSize: 48, bold: true, color: WHITE, fontFace: "Arial",
  margin: 0
});

// 副标题
s1.addText("小红书反指系统 · Week 1 起跑", {
  x: 0.8, y: 2.6, w: 8.4, h: 0.5,
  fontSize: 22, color: ICE_BLUE, fontFace: "Arial",
  margin: 0
});

// 底部信息
s1.addText("2026.05.20  |  LSM · QBW · LELE", {
  x: 0.8, y: 4.8, w: 8.4, h: 0.4,
  fontSize: 14, color: ICE_BLUE, fontFace: "Arial",
  margin: 0
});

// 底部分割线
s1.addShape(pres.shapes.RECTANGLE, {
  x: 0.8, y: 5.2, w: 2.5, h: 0.04,
  fill: { color: ICE_BLUE }
});

// ============================================
// 第 2 页 | 一句话项目 (浅色底)
// ============================================
let s2 = pres.addSlide();
s2.background = { color: WHITE };

// 左侧装饰条
s2.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s2.addText("一句话项目", {
  x: 0.6, y: 0.4, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial",
  margin: 0
});

// 引用框
s2.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.2, w: 8.8, h: 1.6,
  fill: { color: LIGHT_BG },
  line: { color: ICE_BLUE, width: 1.5 }
});

s2.addText("对小红书上指定 ticker 的相关帖子进行多模态情绪打分，日度聚合输出\"乐观/悲观\"和\"讨论量\"两个指标，辅助人工交易决策。", {
  x: 0.9, y: 1.4, w: 8.2, h: 1.2,
  fontSize: 16, color: "334155", fontFace: "Arial",
  valign: "middle", margin: 0
});

// 三列要点
s2.addText([
  { text: "核心产出", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "DailyMetric（SQLite 日度指标表）", options: { color: "475569" } }
], { x: 0.6, y: 3.2, w: 2.7, h: 1.0, fontSize: 13, margin: 0 });

s2.addText([
  { text: "技术路线", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "LLM 多模态打分 → 日度聚合 → 回测验证 → Dashboard 可视化", options: { color: "475569" } }
], { x: 3.6, y: 3.2, w: 3.0, h: 1.0, fontSize: 13, margin: 0 });

s2.addText([
  { text: "当前阶段", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "Week 1 M1（端到端骨架打通）", options: { color: "475569" } }
], { x: 6.9, y: 3.2, w: 2.5, h: 1.0, fontSize: 13, margin: 0 });

// ============================================
// 第 3 页 | 系统架构总览
// ============================================
let s3 = pres.addSlide();
s3.background = { color: WHITE };

s3.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s3.addText("系统架构总览", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

s3.addText("7 模块 · 只走 JSON / SQLite · 不互相 import", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

const modules = [
  { id: "M1", name: "Scraper",      desc: "数据采集",    color: "0D9488" },
  { id: "M2", name: "Sentiment",    desc: "情绪打分",    color: "0891B2" },
  { id: "M3", name: "Aggregator",   desc: "日度聚合",    color: "2563EB" },
  { id: "M4", name: "Eval Bench",   desc: "模型选型",    color: "7C3AED" },
  { id: "M5", name: "Backtest",     desc: "信号验证",    color: "DB2777" },
  { id: "M6", name: "Dashboard",    desc: "可视化",      color: "EA580C" },
  { id: "M7", name: "Notify",       desc: "告警推送",    color: "DC2626" },
];

const startX = 0.6;
const boxW = 1.2;
const boxH = 0.9;
const gap = 0.15;

modules.forEach((m, i) => {
  const bx = startX + i * (boxW + gap);
  const by = 1.8;

  // 模块卡片背景
  s3.addShape(pres.shapes.RECTANGLE, {
    x: bx, y: by, w: boxW, h: boxH,
    fill: { color: m.color },
    shadow: makeShadow()
  });

  // 模块 ID
  s3.addText(m.id, {
    x: bx, y: by + 0.1, w: boxW, h: 0.3,
    fontSize: 18, bold: true, color: WHITE,
    align: "center", fontFace: "Arial", margin: 0
  });

  // 模块名
  s3.addText(m.name, {
    x: bx, y: by + 0.4, w: boxW, h: 0.25,
    fontSize: 11, color: WHITE,
    align: "center", fontFace: "Arial", margin: 0
  });

  // 描述（卡片下方）
  s3.addText(m.desc, {
    x: bx, y: by + boxH + 0.1, w: boxW, h: 0.3,
    fontSize: 10, color: "475569",
    align: "center", fontFace: "Arial", margin: 0
  });

  // 箭头（最后一个不用）
  if (i < modules.length - 1) {
    s3.addShape(pres.shapes.RECTANGLE, {
      x: bx + boxW + 0.02, y: by + boxH / 2 - 0.04, w: gap - 0.04, h: 0.08,
      fill: { color: "CBD5E1" }
    });
    // 小三角箭头
    s3.addShape(pres.shapes.RECTANGLE, {
      x: bx + boxW + gap - 0.1, y: by + boxH / 2 - 0.08, w: 0.1, h: 0.16,
      fill: { color: "CBD5E1" }
    });
  }
});

// 数据流说明
s3.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 3.6, w: 8.8, h: 1.6,
  fill: { color: LIGHT_BG }
});

s3.addText([
  { text: "数据流", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "M1 → data/raw/*.jsonl  →  M2 → data/scored/*.jsonl  →  M3 → SQLite daily_metrics", options: { color: "475569", breakLine: true } },
  { text: "M4 读 labeled_200.csv 评测  |  M5 读 SQLite + yfinance 回测  |  M6/M7 消费 SQLite", options: { color: "475569" } }
], { x: 0.8, y: 3.75, w: 8.4, h: 1.3, fontSize: 12, margin: 0 });

// ============================================
// 第 4 页 | 团队分工
// ============================================
let s4 = pres.addSlide();
s4.background = { color: WHITE };

s4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s4.addText("团队分工", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

s4.addText("3 人 × 4 块", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 表格
s4.addTable([
  [
    { text: "负责人", options: { bold: true, fill: { color: NAVY }, color: WHITE, align: "center" } },
    { text: "模块",     options: { bold: true, fill: { color: NAVY }, color: WHITE, align: "center" } },
    { text: "核心交付", options: { bold: true, fill: { color: NAVY }, color: WHITE, align: "center" } }
  ],
  ["A", "M1 Scraper", "每日 ≥40 条 RawPost，ManualScraper 兜底"],
  ["B", "M2 + M3 + M4", "打分质量闭环：prompt → 聚合 → 评测"],
  ["C", "M5 Backtest", "90 天 IC + 事件研究"],
  ["C", "M6 + M7", "Dashboard + Notify 告警"],
], {
  x: 0.6, y: 1.5, w: 8.8, h: 2.8,
  colW: [1.5, 2.5, 4.8],
  border: { pt: 0.5, color: "E2E8F0" },
  fontSize: 13,
  fontFace: "Arial",
  color: "334155",
  valign: "middle"
});

// ============================================
// 第 5 页 | 模块定义速览 (M1-M4)
// ============================================
let s5 = pres.addSlide();
s5.background = { color: WHITE };

s5.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s5.addText("模块定义速览", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

s5.addText("Week 1-2 重点模块", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

const mDefs = [
  { id: "M1", title: "Scraper",        color: "0D9488",
    body: "keyword + 日期 → data/raw/{date}_{keyword}.jsonl\nManualScraper 兜底，Scraper 断更 12h 内自动降级" },
  { id: "M2", title: "Sentiment",      color: "0891B2",
    body: "analyze(post) → ScoredPost\npost / comment 分开打分，polarity 五档（-2 ~ +2）\n必须输出 is_relevant 门控 + quote 证据" },
  { id: "M3", title: "Aggregator",     color: "2563EB",
    body: "roll_up(date) → DailyMetric → SQLite\nn_likes 加权平均，只 count is_relevant=true" },
  { id: "M4", title: "Eval Bench",     color: "7C3AED",
    body: "200 条人工标注，横评多模型\nClaude / GPT-4o / DeepSeek / Qwen\n反讽子集 ≥70% 才上线" },
];

mDefs.forEach((m, i) => {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const cx = 0.6 + col * 4.5;
  const cy = 1.5 + row * 1.9;

  // 卡片背景
  s5.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: 4.3, h: 1.7,
    fill: { color: WHITE },
    line: { color: "E2E8F0", width: 1 },
    shadow: makeShadow()
  });

  // 左侧色条
  s5.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: 0.1, h: 1.7,
    fill: { color: m.color }
  });

  // ID badge
  s5.addShape(pres.shapes.RECTANGLE, {
    x: cx + 0.25, y: cy + 0.15, w: 0.5, h: 0.28,
    fill: { color: m.color }
  });
  s5.addText(m.id, {
    x: cx + 0.25, y: cy + 0.15, w: 0.5, h: 0.28,
    fontSize: 11, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });

  // 标题
  s5.addText(m.title, {
    x: cx + 0.85, y: cy + 0.15, w: 3.2, h: 0.3,
    fontSize: 15, bold: true, color: NAVY, fontFace: "Arial", margin: 0
  });

  // 内容
  s5.addText(m.body, {
    x: cx + 0.25, y: cy + 0.55, w: 3.9, h: 1.0,
    fontSize: 11, color: "475569", fontFace: "Arial",
    valign: "top", margin: 0
  });
});

// ============================================
// 第 6 页 | 数据契约
// ============================================
let s6 = pres.addSlide();
s6.background = { color: WHITE };

s6.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s6.addText("数据契约", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

s6.addText("最重要的部分 —— 不改这里，大家并行开发", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

const contracts = [
  { name: "RawPost",        flow: "M1 → M2",      color: "0D9488",
    items: ["post_id, keyword, date", "author, text, image_urls", "n_likes, n_comments_total", "comments[].text, comments[].n_likes"] },
  { name: "ScoredPost",     flow: "M2 → M3",      color: "0891B2",
    items: ["is_relevant, sentiment_post", "comment_scores[]", "sentiment_comments_avg", "fomo, quote, model, cost_usd"] },
  { name: "DailyMetric",    flow: "M3 → SQLite",  color: "2563EB",
    items: ["ticker, date (PK)", "n_posts", "sentiment_post_avg", "sentiment_comment_avg", "sentiment_combined", "top_quotes_json"] },
];

contracts.forEach((c, i) => {
  const cx = 0.6 + i * 3.05;
  const cy = 1.5;

  // 卡片
  s6.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: 2.9, h: 3.4,
    fill: { color: LIGHT_BG },
    line: { color: "E2E8F0", width: 1 }
  });

  // 顶部色条
  s6.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: 2.9, h: 0.12,
    fill: { color: c.color }
  });

  // 契约名
  s6.addText(c.name, {
    x: cx + 0.15, y: cy + 0.25, w: 2.6, h: 0.35,
    fontSize: 16, bold: true, color: NAVY, fontFace: "Arial", margin: 0
  });

  // 流向
  s6.addText(c.flow, {
    x: cx + 0.15, y: cy + 0.6, w: 2.6, h: 0.25,
    fontSize: 11, color: c.color, fontFace: "Arial", margin: 0
  });

  // 字段列表
  const bulletText = c.items.map(it => ({ text: it, options: { bullet: true, breakLine: true } }));
  bulletText[bulletText.length - 1].options.breakLine = false;

  s6.addText(bulletText, {
    x: cx + 0.15, y: cy + 1.0, w: 2.6, h: 2.2,
    fontSize: 11, color: "475569", fontFace: "Arial", margin: 0
  });
});

// 红线提示
s6.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 5.0, w: 8.8, h: 0.45,
  fill: { color: "FEF2F2" },
  line: { color: "FECACA", width: 1 }
});
s6.addText("红线：src/models.py / config/prompts.yaml / watchlist.yaml / scripts/daily_run.py —— 改之前群里 +1", {
  x: 0.8, y: 5.05, w: 8.4, h: 0.35,
  fontSize: 11, color: "DC2626", fontFace: "Arial", valign: "middle", margin: 0
});

// ============================================
// 第 7 页 | 协作流程
// ============================================
let s7 = pres.addSlide();
s7.background = { color: WHITE };

s7.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s7.addText("协作流程", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

s7.addText("怎么不炸", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 代码块背景
s7.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.4, w: 5.0, h: 2.4,
  fill: { color: "1E293B" }
});

s7.addText([
  { text: "git checkout main && git pull",                       options: { color: "A5B4FC", breakLine: true } },
  { text: "git checkout -b feat/m2-sentiment",                   options: { color: "A5B4FC", breakLine: true } },
  { text: "# ...写代码...",                                      options: { color: "64748B", breakLine: true } },
  { text: "git add src/sentiment/engine.py",                     options: { color: "A5B4FC", breakLine: true } },
  { text: "git commit -m \"M2: first happy path\"",             options: { color: "A5B4FC", breakLine: true } },
  { text: "git push -u origin feat/m2-sentiment",                options: { color: "A5B4FC", breakLine: true } },
  { text: "# PR 网页发，按模板 4 问填",                         options: { color: "64748B", breakLine: true } },
], {
  x: 0.8, y: 1.55, w: 4.6, h: 2.1,
  fontSize: 11, fontFace: "Consolas", margin: 0
});

// 右侧要点
const rules = [
  { head: "永远不直推 main",           body: "所有改动走 feature 分支 + PR" },
  { head: "核心文件改前群里 +1",        body: "models.py / prompts.yaml / watchlist.yaml / daily_run.py" },
  { head: "模块边界不越界",            body: "谁的模块谁写测试，不要改别人的目录" },
  { head: "PR 描述按模板 4 问",         body: "改了什么 / happy path / 核心文件 / pyproject.toml" },
];

rules.forEach((r, i) => {
  const ry = 1.4 + i * 0.95;

  // 序号圆圈
  s7.addShape(pres.shapes.OVAL, {
    x: 5.9, y: ry, w: 0.35, h: 0.35,
    fill: { color: NAVY }
  });
  s7.addText(String(i + 1), {
    x: 5.9, y: ry, w: 0.35, h: 0.35,
    fontSize: 12, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });

  s7.addText(r.head, {
    x: 6.4, y: ry, w: 3.0, h: 0.3,
    fontSize: 13, bold: true, color: NAVY, fontFace: "Arial", margin: 0
  });
  s7.addText(r.body, {
    x: 6.4, y: ry + 0.3, w: 3.0, h: 0.4,
    fontSize: 11, color: "475569", fontFace: "Arial", margin: 0
  });
});

// ============================================
// 输出
// ============================================
pres.writeFile({ fileName: "report/20260520_启动会.pptx" });
console.log("Generated: report/20260520_启动会.pptx");
