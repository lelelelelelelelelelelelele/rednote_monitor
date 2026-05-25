const pptxgen = require("C:/Users/ADMIN/AppData/Roaming/npm/node_modules/pptxgenjs");

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
s1.addText("小红书散户情绪反指系统", {
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
// 第 2 页 | 项目简介 (浅色底)
// ============================================
let s2 = pres.addSlide();
s2.background = { color: WHITE };

// 左侧装饰条
s2.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s2.addText("项目简介", {
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
  { text: "输出什么", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "DailyMetric（SQLite 日度指标表）", options: { color: "475569" } }
], { x: 0.6, y: 3.2, w: 2.7, h: 1.0, fontSize: 13, margin: 0 });

s2.addText([
  { text: "怎么实现", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "LLM 多模态打分 → 日度聚合 → 回测验证 → Dashboard 可视化", options: { color: "475569" } }
], { x: 3.6, y: 3.2, w: 3.0, h: 1.0, fontSize: 13, margin: 0 });

s2.addText([
  { text: "现在到哪了", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "Week 1 M1（端到端骨架打通）", options: { color: "475569" } }
], { x: 6.9, y: 3.2, w: 2.5, h: 1.0, fontSize: 13, margin: 0 });

// ============================================
// 第 3 页 | 🤖 AI 友好声明
// ============================================
let sAI = pres.addSlide();
sAI.background = { color: WHITE };

// 左侧装饰条
sAI.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

sAI.addText("AI 友好声明", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

sAI.addText("这是一个 vibe-coding 项目 · AI 是一等公民", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 三张卡片横排
const aiCards = [
  {
    color: "0D9488", emoji: "✍️",
    title: "AI 写代码",
    body: "commit / PR / issue 都行，标好 Co-Authored-By 就 OK，不用刻意\"伪装人写的\"。"
  },
  {
    color: "0891B2", emoji: "🧰",
    title: "AI 工具链",
    body: "cc / Cursor / Codex / ChatGPT 任选；BLUEPRINT.md + CLAUDE.md 是给 AI 看的真值文档，改这两份等于给所有人的 AI 同步。"
  },
  {
    color: "7C3AED", emoji: "🚧",
    title: "协作的边界",
    body: "写代码很自由；改 4 个核心受保护文件走 PR 大家看一下；架构方向最终人拍板，AI 是助手不是 owner。"
  },
];

{
const aiCardW = 2.8, aiCardH = 2.7, aiGap = 0.2;
aiCards.forEach((c, i) => {
  const cx = 0.6 + i * (aiCardW + aiGap);
  const cy = 1.5;

  // 卡片底
  sAI.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: aiCardW, h: aiCardH,
    fill: { color: WHITE },
    line: { color: "E2E8F0", width: 1 },
    shadow: makeShadow()
  });

  // 顶部色条
  sAI.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: aiCardW, h: 0.12,
    fill: { color: c.color }
  });

  // emoji
  sAI.addText(c.emoji, {
    x: cx + 0.2, y: cy + 0.3, w: 0.55, h: 0.6,
    fontSize: 22, fontFace: "Arial", valign: "middle", margin: 0
  });

  // 标题
  sAI.addText(c.title, {
    x: cx + 0.75, y: cy + 0.3, w: aiCardW - 0.85, h: 0.6,
    fontSize: 15, bold: true, color: NAVY, fontFace: "Arial",
    valign: "middle", margin: 0
  });

  // 正文
  sAI.addText(c.body, {
    x: cx + 0.25, y: cy + 1.0, w: aiCardW - 0.4, h: aiCardH - 1.1,
    fontSize: 12, color: "334155", fontFace: "Arial",
    valign: "top", margin: 0, paraSpaceAfter: 4
  });
});
}

// 底部 why bar
sAI.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.55, w: 8.8, h: 0.75,
  fill: { color: LIGHT_BG },
  line: { color: "E2E8F0", width: 1 }
});
sAI.addText([
  { text: "为啥强调这点：", options: { bold: true, color: NAVY } },
  { text: "团队规模小、节奏快、同学开发经验深浅不一 —— AI 把门槛拉平，让大家把精力放在判断和设计上，不在语法和样板代码上。", options: { color: "475569" } }
], {
  x: 0.8, y: 4.6, w: 8.4, h: 0.65,
  fontSize: 11, fontFace: "Arial", valign: "middle", margin: 0
});

// ============================================
// 第 4 页 | 系统架构总览
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

s3.addText("7 个模块 · JSON / SQLite 传递 · 不互相 import", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 架构图 (1536x1024, aspect 1.5)
const imgW = 4.2;
const imgH = imgW / 1.5;
const imgX = (10 - imgW) / 2;
const imgY = 1.1;

s3.addImage({
  path: "E:/project/rednote_monitor/docs/architecture/diagram.png",
  x: imgX, y: imgY, w: imgW, h: imgH,
  sizing: { type: "contain", w: imgW, h: imgH }
});

// 模块标签网格（图下方，4+3 两行，无箭头）
const modules = [
  { id: "M1", name: "Scraper",    color: "0D9488" },
  { id: "M2", name: "Sentiment",  color: "0891B2" },
  { id: "M3", name: "Aggregator", color: "2563EB" },
  { id: "M4", name: "Eval",       color: "7C3AED" },
  { id: "M5", name: "Backtest",   color: "DB2777" },
  { id: "M6", name: "Dashboard",  color: "EA580C" },
  { id: "M7", name: "Notify",     color: "DC2626" },
];

const tagW = 1.1;
const tagH = 0.32;
const tagGap = 0.12;
const row1Y = imgY + imgH + 0.3;
const row2Y = row1Y + tagH + 0.15;
const row1StartX = (10 - (4 * tagW + 3 * tagGap)) / 2;
const row2StartX = (10 - (3 * tagW + 2 * tagGap)) / 2;

modules.forEach((m, i) => {
  const row = i < 4 ? 0 : 1;
  const col = i < 4 ? i : i - 4;
  const startX = row === 0 ? row1StartX : row2StartX;
  const tx = startX + col * (tagW + tagGap);
  const ty = row === 0 ? row1Y : row2Y;

  s3.addShape(pres.shapes.RECTANGLE, {
    x: tx, y: ty, w: tagW, h: tagH,
    fill: { color: m.color },
    rectRadius: 0.05
  });
  s3.addText(`${m.id} ${m.name}`, {
    x: tx, y: ty, w: tagW, h: tagH,
    fontSize: 10, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });
});

// ============================================
// 第 5 页 | 团队分工
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

s4.addText("模块归属（M6 + M7 Week 2 末再分）", {
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
  ["LSM",  "M2 + M3 + M4",  "打分质量闭环：prompt → 聚合 → 评测"],
  ["LELE", "M1（暂时）",      "每日 ≥40 条 RawPost，ManualScraper 兜底"],
  ["QBW",  "M5 Backtest",   "90 天 IC + 事件研究"],
  [{ text: "待定", options: { color: "94A3B8", italic: true } },
   { text: "M6 + M7", options: { color: "94A3B8", italic: true } },
   { text: "Dashboard + Notify（Week 2 末再分）", options: { color: "94A3B8", italic: true } }],
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
// 第 6 页 | 关键设计决策（端口解耦 + 协议确定）
// ============================================
let s5 = pres.addSlide();
s5.background = { color: WHITE };

s5.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s5.addText("关键设计决策", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

s5.addText("模块能并行的两条腿：端口解耦 + 协议确定", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 左卡片：端口解耦
const leftX = 0.6, cardY = 1.4, cardW = 4.3, cardH = 2.3;
s5.addShape(pres.shapes.RECTANGLE, {
  x: leftX, y: cardY, w: cardW, h: cardH,
  fill: { color: WHITE },
  line: { color: "E2E8F0", width: 1 },
  shadow: makeShadow()
});
s5.addShape(pres.shapes.RECTANGLE, {
  x: leftX, y: cardY, w: cardW, h: 0.12,
  fill: { color: "0D9488" }
});
s5.addText("端口解耦", {
  x: leftX + 0.25, y: cardY + 0.25, w: cardW - 0.5, h: 0.4,
  fontSize: 18, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s5.addText("模块之间不互相 import", {
  x: leftX + 0.25, y: cardY + 0.65, w: cardW - 0.5, h: 0.25,
  fontSize: 11, color: "0D9488", fontFace: "Arial", margin: 0
});
s5.addText([
  { text: "只走 JSON 文件 / SQLite 传递", options: { bullet: true, breakLine: true } },
  { text: "模块间无 Python import 依赖", options: { bullet: true, breakLine: true } },
  { text: "接口冻结后，内部实现随便改", options: { bullet: true, breakLine: true } },
  { text: "7 个模块的并行排期靠这个", options: { bullet: true, breakLine: false } },
], {
  x: leftX + 0.25, y: cardY + 1.0, w: cardW - 0.4, h: 1.2,
  fontSize: 12, color: "475569", fontFace: "Arial", margin: 0
});

// 右卡片：协议确定
const rightX = 5.1;
s5.addShape(pres.shapes.RECTANGLE, {
  x: rightX, y: cardY, w: cardW, h: cardH,
  fill: { color: WHITE },
  line: { color: "E2E8F0", width: 1 },
  shadow: makeShadow()
});
s5.addShape(pres.shapes.RECTANGLE, {
  x: rightX, y: cardY, w: cardW, h: 0.12,
  fill: { color: "2563EB" }
});
s5.addText("协议确定", {
  x: rightX + 0.25, y: cardY + 0.25, w: cardW - 0.5, h: 0.4,
  fontSize: 18, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s5.addText("3 份数据契约 + 4 个红线文件", {
  x: rightX + 0.25, y: cardY + 0.65, w: cardW - 0.5, h: 0.25,
  fontSize: 11, color: "2563EB", fontFace: "Arial", margin: 0
});
s5.addText([
  { text: "RawPost",     options: { bold: true, color: "0D9488" } },
  { text: "  M1 → M2", options: { color: "475569", breakLine: true } },
  { text: "ScoredPost",  options: { bold: true, color: "0891B2" } },
  { text: "  M2 → M3", options: { color: "475569", breakLine: true } },
  { text: "DailyMetric", options: { bold: true, color: "2563EB" } },
  { text: "  M3 → SQLite", options: { color: "475569", breakLine: false } },
], {
  x: rightX + 0.25, y: cardY + 1.0, w: cardW - 0.4, h: 1.2,
  fontSize: 12, fontFace: "Arial", margin: 0, paraSpaceAfter: 4
});

// 红线提示条
s5.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 3.85, w: 8.8, h: 0.45,
  fill: { color: "FEF2F2" },
  line: { color: "FECACA", width: 1 }
});
s5.addText("红线：models.py / prompts.yaml / watchlist.yaml / daily_run.py — 改前群里 +1", {
  x: 0.8, y: 3.9, w: 8.4, h: 0.35,
  fontSize: 11, color: "DC2626", fontFace: "Arial", valign: "middle", margin: 0
});

// 底部三条非显然约定
const chips = [
  { head: "post / comment 分开打分", body: "XHS 上常常情绪相反" },
  { head: "is_relevant 门控",         body: "宽 keyword 噪声实测 ~50%" },
  { head: "反讽 ≥70% 才上线",         body: "M4 兜底，不达标不发布" },
];
chips.forEach((c, i) => {
  const chipX = 0.6 + i * 3.0;
  const chipY = 4.55;
  const chipW = 2.85;
  s5.addShape(pres.shapes.RECTANGLE, {
    x: chipX, y: chipY, w: chipW, h: 0.85,
    fill: { color: LIGHT_BG },
    line: { color: "E2E8F0", width: 1 }
  });
  s5.addText(c.head, {
    x: chipX + 0.15, y: chipY + 0.08, w: chipW - 0.3, h: 0.35,
    fontSize: 12, bold: true, color: NAVY, fontFace: "Arial", margin: 0
  });
  s5.addText(c.body, {
    x: chipX + 0.15, y: chipY + 0.43, w: chipW - 0.3, h: 0.35,
    fontSize: 10, color: "64748B", fontFace: "Arial", margin: 0
  });
});

// ============================================
// 第 7 页 | 协作流程
// ============================================
let s6 = pres.addSlide();
s6.background = { color: WHITE };

s6.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s6.addText("协作流程", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

s6.addText("怎么不炸", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 代码块背景
s6.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.4, w: 5.0, h: 2.4,
  fill: { color: "1E293B" }
});

s6.addText([
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
  s6.addShape(pres.shapes.OVAL, {
    x: 5.9, y: ry, w: 0.35, h: 0.35,
    fill: { color: NAVY }
  });
  s6.addText(String(i + 1), {
    x: 5.9, y: ry, w: 0.35, h: 0.35,
    fontSize: 12, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });

  s6.addText(r.head, {
    x: 6.4, y: ry, w: 3.0, h: 0.3,
    fontSize: 13, bold: true, color: NAVY, fontFace: "Arial", margin: 0
  });
  s6.addText(r.body, {
    x: 6.4, y: ry + 0.3, w: 3.0, h: 0.4,
    fontSize: 11, color: "475569", fontFace: "Arial", margin: 0
  });
});

// ============================================
// 第 8 页 | 周演示 · 欢迎角度
// ============================================
let s7 = pres.addSlide();
s7.background = { color: WHITE };

s7.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s7.addText("周演示 · 欢迎角度", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

s7.addText("这几点都欢迎聊，自由发挥，没卡到的角度跳过没事", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

const overview = [
  { num: "1", emoji: "📐", title: "架构图",   color: "0D9488", line: "自己模块的子架构 · 本周演化" },
  { num: "2", emoji: "🚀", title: "进展",     color: "0891B2", line: "对应模块讲，量化结果" },
  { num: "3", emoji: "✅", title: "To-do",   color: "2563EB", line: "挂钩模块块 + 遇到的卡点" },
  { num: "4", emoji: "📊", title: "Token",   color: "7C3AED", line: "ccusage 数据，看烧在哪儿" },
  { num: "5", emoji: "❓", title: "Q&A",     color: "EA580C", line: "具体卡点 1-2 个就好" },
];

{
const cardW = 2.85, cardH = 1.5;

overview.forEach((s, i) => {
  let cx, cy;
  if (i < 3) {
    cx = 0.6 + i * (cardW + 0.15);
    cy = 1.4;
  } else {
    const j = i - 3;
    cx = 2.0 + j * (cardW + 0.3);
    cy = 1.4 + cardH + 0.15;
  }

  // 卡片
  s7.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: cardW, h: cardH,
    fill: { color: WHITE },
    line: { color: "E2E8F0", width: 1 },
    shadow: makeShadow()
  });

  // 顶部色条
  s7.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: cardW, h: 0.12,
    fill: { color: s.color }
  });

  // 编号圆圈
  s7.addShape(pres.shapes.OVAL, {
    x: cx + 0.2, y: cy + 0.3, w: 0.4, h: 0.4,
    fill: { color: s.color }
  });
  s7.addText(s.num, {
    x: cx + 0.2, y: cy + 0.3, w: 0.4, h: 0.4,
    fontSize: 14, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });

  // emoji + 标题
  s7.addText(`${s.emoji}  ${s.title}`, {
    x: cx + 0.7, y: cy + 0.3, w: cardW - 0.85, h: 0.4,
    fontSize: 15, bold: true, color: NAVY, fontFace: "Arial",
    valign: "middle", margin: 0
  });

  // 一句话
  s7.addText(s.line, {
    x: cx + 0.25, y: cy + 0.85, w: cardW - 0.4, h: 0.55,
    fontSize: 11, color: "475569", fontFace: "Arial",
    valign: "top", margin: 0
  });
});
}

// 底部 why bar
s7.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.75, w: 8.8, h: 0.55,
  fill: { color: LIGHT_BG },
  line: { color: "E2E8F0", width: 1 }
});
s7.addText([
  { text: "为什么列这五个角度：", options: { bold: true, color: NAVY } },
  { text: "架构 → 进展 → 计划 → 烧在哪 → 卡点，从宏观到细节顺一遍。讲多讲少看心情，vibe-coding 项目不打卡。", options: { color: "475569" } }
], {
  x: 0.8, y: 4.8, w: 8.4, h: 0.45,
  fontSize: 11, fontFace: "Arial", valign: "middle", margin: 0
});

// ============================================
// 第 9-13 页 | 周演示五件事 · 逐项展开
// ============================================
const demoDetails = [
  {
    num: 1, emoji: "📐", title: "架构图", color: "0D9488",
    purpose: "讲自己模块的子架构图（不是顶层 BLUEPRINT），让大家看到你这块怎么搭、本周怎么演化",
    how: [
      "架构是分层的：顶层 BLUEPRINT 一张总图 + 每个模块自己一张 sub-diagram",
      "重点讲本周这张子图变了哪里、为什么变",
      "顶层 BLUEPRINT 有人动了再单独提，不用每周复述"
    ],
    quote: "我这周 M2 内部把 sentiment engine 拆成了 prompt-builder + llm-caller + parser 三块，目的是把 prompt 调优和 LLM 调用解耦 —— 下周横评不同模型时 prompt-builder 这部分不用动。"
  },
  {
    num: 2, emoji: "🚀", title: "进展", color: "0891B2",
    purpose: "展示产出，同步状态",
    how: [
      "对应架构图的模块来讲",
      "格式：[模块名] 完成了什么 + 结果如何"
    ],
    quote: "M1 采集模块：本周完成了对小红书新接口的适配，抓取成功率从 80% 提升到了 98%。"
  },
  {
    num: 3, emoji: "✅", title: "To-do", color: "2563EB",
    purpose: "同步下周计划，挂钩到模块块 + 本周遇到的卡点",
    how: [
      "挂到具体模块（M1-M7），讲想推进到哪一步",
      "顺带说一下踩到了啥卡点 / 担心啥 / 想怎么绕",
      "不用列 Token 预算 —— token 是共享池，不抢不排名"
    ],
    quote: "下周继续推 M2 sentiment engine，想把 prompt 在反讽子集上准确率从 65% 提到 75%。担心的是 GPT-4o-mini 对反讽可能就这天花板了，如果不行就上 Sonnet 横评对比。"
  },
  {
    num: 4, emoji: "📊", title: "Token 用量", color: "7C3AED",
    purpose: "token 花费 ≈ 这周投入的粗略指标 — 看大家精力砸在哪个模块、哪个任务上",
    how: [
      "数据来源：ccusage",
      "自己烧得多 / 少在哪个模块、哪个任务上，有没有意外发现",
      "注意：token 反映投入不等于产出（试错、重跑也烧），但作为\"这周做了多少事\"的粗看够用"
    ],
    quote: "本周 M2 prompt 调优跑了好几轮，大概 120k；意外发现 vision 调用单价比纯文本贵 3x，下次准备先在文本-only 上 iterate 收敛了再上图。"
  },
  {
    num: 5, emoji: "❓", title: "Q&A", color: "EA580C",
    purpose: "解决卡点 — 只针对本周遇到的实际问题讨论，不做开放式建议征询、不发散",
    how: [
      "提前准备 1-2 个具体卡住的问题",
      "描述清楚：已经尝试过什么、卡在哪、自己的备选方案",
      "没卡点直接跳过，比硬凑话题好"
    ],
    quote: "本周 M2 跑评论打分时，LLM 偶尔返回非 JSON 字符串，目前是 try/except 兜底，命中率约 3%。想问一下大家有没有更稳的 prompt 收敛方法。"
  },
];

demoDetails.forEach((sec) => {
  const sl = pres.addSlide();
  sl.background = { color: WHITE };

  // 左侧装饰条
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.15, h: 5.625,
    fill: { color: NAVY }
  });

  // 标题: 名称（emoji 不放主标题，PowerPoint 渲染会飘）
  sl.addText(sec.title, {
    x: 0.6, y: 0.35, w: 8.8, h: 0.6,
    fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
  });

  // 副标题: 序号 / 5
  sl.addText(`周演示 · 欢迎角度 · ${sec.num} / 5`, {
    x: 0.6, y: 0.95, w: 8.8, h: 0.3,
    fontSize: 13, color: sec.color, fontFace: "Arial", margin: 0
  });

  // 目的 tag
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.45, w: 0.75, h: 0.32,
    fill: { color: sec.color }
  });
  sl.addText("目的", {
    x: 0.6, y: 1.45, w: 0.75, h: 0.32,
    fontSize: 12, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });
  sl.addText(sec.purpose, {
    x: 1.45, y: 1.45, w: 7.95, h: 0.32,
    fontSize: 13, bold: true, color: NAVY, fontFace: "Arial",
    valign: "middle", margin: 0
  });

  // 怎么讲 tag
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 2.0, w: 0.75, h: 0.32,
    fill: { color: sec.color }
  });
  sl.addText("怎么讲", {
    x: 0.6, y: 2.0, w: 0.75, h: 0.32,
    fontSize: 12, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });
  const howBullets = sec.how.map((t, i) => ({
    text: t,
    options: { bullet: true, breakLine: i < sec.how.length - 1 }
  }));
  sl.addText(howBullets, {
    x: 1.45, y: 2.0, w: 7.95, h: 1.4,
    fontSize: 13, color: "334155", fontFace: "Arial",
    valign: "top", margin: 0, paraSpaceAfter: 6
  });

  // 话术示例 (高亮卡片)
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 3.6, w: 8.8, h: 1.7,
    fill: { color: LIGHT_BG },
    line: { color: sec.color, width: 1.5 }
  });
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 3.6, w: 0.08, h: 1.7,
    fill: { color: sec.color }
  });
  sl.addText("话术示例", {
    x: 0.85, y: 3.7, w: 3.0, h: 0.3,
    fontSize: 11, bold: true, color: sec.color, fontFace: "Arial", margin: 0
  });
  sl.addText(`"${sec.quote}"`, {
    x: 0.85, y: 4.05, w: 8.4, h: 1.15,
    fontSize: 13, color: "334155", fontFace: "Arial", italic: true,
    valign: "top", margin: 0
  });
});

// ============================================
// 输出
// ============================================
pres.writeFile({ fileName: "20260520_启动会.pptx" });
console.log("Generated: report/20260520_启动会.pptx");
