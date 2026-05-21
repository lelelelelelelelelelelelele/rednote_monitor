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
pres.title = "AI 工具使用指南";

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
s1.addText("AI 工具使用指南", {
  x: 0.8, y: 1.6, w: 8.4, h: 0.9,
  fontSize: 48, bold: true, color: WHITE, fontFace: "Arial",
  margin: 0
});

// 副标题
s1.addText("Git · CC Usage · PPT 技能分享", {
  x: 0.8, y: 2.6, w: 8.4, h: 0.5,
  fontSize: 22, color: ICE_BLUE, fontFace: "Arial",
  margin: 0
});

// 底部信息
s1.addText("2026.05.20", {
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
// 第 2 页 | 为什么写这份指南
// ============================================
let s2 = pres.addSlide();
s2.background = { color: WHITE };

s2.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s2.addText("为什么写这份指南", {
  x: 0.6, y: 0.4, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial",
  margin: 0
});

// 左：团队现状
s2.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.3, w: 4.2, h: 2.0,
  fill: { color: LIGHT_BG },
  line: { color: ICE_BLUE, width: 1.5 }
});
s2.addText([
  { text: "团队现状", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "· 3 人协作，项目节奏快", options: { color: "475569", breakLine: true } },
  { text: "· 部分同学较少接触 AI 工具", options: { color: "475569", breakLine: true } },
  { text: "· 用好工具 = 把时间花在判断上", options: { color: "475569" } }
], { x: 0.8, y: 1.5, w: 3.8, h: 1.6, fontSize: 13, margin: 0 });

// 右：三个核心场景
s2.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 1.3, w: 4.2, h: 2.0,
  fill: { color: LIGHT_BG },
  line: { color: ICE_BLUE, width: 1.5 }
});
s2.addText([
  { text: "三个核心场景", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "1. Git — 代码协作不炸", options: { color: "475569", breakLine: true } },
  { text: "2. CC Usage — 花明白钱", options: { color: "475569", breakLine: true } },
  { text: "3. AI 做 PPT — 汇报快速产出", options: { color: "475569" } }
], { x: 5.4, y: 1.5, w: 3.8, h: 1.6, fontSize: 13, margin: 0 });

// ============================================
// 第 3 页 | Git（1/3）为什么必须学
// ============================================
let s3 = pres.addSlide();
s3.background = { color: WHITE };

s3.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s3.addText("Git 极简工作流", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s3.addText("（1/3）为什么必须学", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 左：没有版本控制的痛
s3.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.5, w: 4.2, h: 3.0,
  fill: { color: "FEF2F2" },
  line: { color: "FECACA", width: 1 }
});
s3.addText([
  { text: "没有版本控制的痛", options: { bold: true, color: "DC2626", breakLine: true } },
  { text: "· 文件叫 final_v2_真的final_不改了.docx", options: { color: "475569", breakLine: true } },
  { text: "· 谁改了哪行、为什么改，找不到", options: { color: "475569", breakLine: true } },
  { text: "· 三人同时改，覆盖来覆盖去", options: { color: "475569" } }
], { x: 0.8, y: 1.7, w: 3.8, h: 2.5, fontSize: 13, margin: 0 });

// 右：Git 解决什么
s3.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 1.5, w: 4.2, h: 3.0,
  fill: { color: "F0FDF4" },
  line: { color: "86EFAC", width: 1 }
});
s3.addText([
  { text: "Git 解决什么", options: { bold: true, color: "16A34A", breakLine: true } },
  { text: "· 时光机：回到任何历史版本", options: { color: "475569", breakLine: true } },
  { text: "· 协作：三人并行，自动合并", options: { color: "475569", breakLine: true } },
  { text: "· 问责：谁写的、何时写的，清清楚楚", options: { color: "475569" } }
], { x: 5.4, y: 1.7, w: 3.8, h: 2.5, fontSize: 13, margin: 0 });

// ============================================
// 第 4 页 | Git（2/3）5 个够用命令
// ============================================
let s4 = pres.addSlide();
s4.background = { color: WHITE };

s4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s4.addText("Git 极简工作流", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s4.addText("（2/3）5 个够用命令", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 代码块
s4.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.4, w: 5.5, h: 3.6,
  fill: { color: "1E293B" }
});
s4.addText([
  { text: "# 1. 克隆项目（第一次）",            options: { color: "64748B", breakLine: true } },
  { text: "git clone https://github.com/xxx/xxx.git", options: { color: "A5B4FC", breakLine: true } },
  { text: "",                                           options: { breakLine: true } },
  { text: "# 2. 拉最新代码（每次开干前）",      options: { color: "64748B", breakLine: true } },
  { text: "git pull",                                   options: { color: "A5B4FC", breakLine: true } },
  { text: "",                                           options: { breakLine: true } },
  { text: "# 3. 看改了什么",                    options: { color: "64748B", breakLine: true } },
  { text: "git status",                                 options: { color: "A5B4FC", breakLine: true } },
  { text: "",                                           options: { breakLine: true } },
  { text: "# 4. 提交改动（add → commit → push）", options: { color: "64748B", breakLine: true } },
  { text: "git add 文件名",                           options: { color: "A5B4FC", breakLine: true } },
  { text: 'git commit -m "描述你改了什么"',           options: { color: "A5B4FC", breakLine: true } },
  { text: "git push",                                   options: { color: "A5B4FC", breakLine: true } },
  { text: "",                                           options: { breakLine: true } },
  { text: "# 5. 起分支（不要直接推 main）",     options: { color: "64748B", breakLine: true } },
  { text: "git checkout -b feat/功能名",             options: { color: "A5B4FC" } }
], {
  x: 0.8, y: 1.55, w: 5.1, h: 3.3,
  fontSize: 10, fontFace: "Consolas", margin: 0
});

// 右侧：流程图
s4.addShape(pres.shapes.RECTANGLE, {
  x: 6.4, y: 1.4, w: 3.0, h: 3.6,
  fill: { color: LIGHT_BG }
});
s4.addText([
  { text: "记不住？记这张", options: { bold: true, color: NAVY, breakLine: true } }
], { x: 6.6, y: 1.6, w: 2.6, h: 0.4, fontSize: 14, margin: 0 });

const flowSteps = [
  { text: "git pull", color: "2563EB" },
  { text: "↓", color: SLATE },
  { text: "改代码", color: "475569" },
  { text: "↓", color: SLATE },
  { text: "git add", color: "2563EB" },
  { text: "↓", color: SLATE },
  { text: "git commit", color: "2563EB" },
  { text: "↓", color: SLATE },
  { text: "git push", color: "2563EB" }
];
let fy = 2.1;
flowSteps.forEach((step) => {
  s4.addText(step.text, {
    x: 6.6, y: fy, w: 2.6, h: 0.28,
    fontSize: 12, bold: step.color !== SLATE && step.color !== "475569",
    color: step.color, fontFace: "Arial",
    align: "center", margin: 0
  });
  fy += 0.32;
});

// ============================================
// 第 5 页 | Git（3/3）分支规则和常见坑
// ============================================
let s5 = pres.addSlide();
s5.background = { color: WHITE };

s5.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s5.addText("Git 极简工作流", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s5.addText("（3/3）分支规则和常见坑", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 分支命名
s5.addText("分支命名", {
  x: 0.6, y: 1.4, w: 4.0, h: 0.3,
  fontSize: 14, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s5.addText([
  { text: "feat/新功能  →  新功能开发", options: { color: "475569", breakLine: true } },
  { text: "fix/bug描述  →  修 bug", options: { color: "475569", breakLine: true } },
  { text: "docs/文档名  →  改文档", options: { color: "475569" } }
], { x: 0.6, y: 1.75, w: 4.0, h: 1.2, fontSize: 12, margin: 0 });

// 黄金规则
s5.addText("黄金规则", {
  x: 5.0, y: 1.4, w: 4.4, h: 0.3,
  fontSize: 14, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
const rules = [
  "1. 永远不直推 main",
  "2. 每次开干前先 git pull",
  "3. 相关文件一起 commit，不要攒",
  "4. push 不上？先 pull 再 push"
];
rules.forEach((r, i) => {
  s5.addText(r, {
    x: 5.0, y: 1.75 + i * 0.3, w: 4.4, h: 0.28,
    fontSize: 12, color: "475569", fontFace: "Arial", margin: 0
  });
});

// 常见坑表格
s5.addText("常见坑", {
  x: 0.6, y: 3.2, w: 8.8, h: 0.3,
  fontSize: 14, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

s5.addTable([
  [
    { text: "现象", options: { bold: true, fill: { color: NAVY }, color: WHITE, align: "center" } },
    { text: "原因", options: { bold: true, fill: { color: NAVY }, color: WHITE, align: "center" } },
    { text: "解决", options: { bold: true, fill: { color: NAVY }, color: WHITE, align: "center" } }
  ],
  ["push 被拒", "main 有更新", "先 pull，再 push"],
  ["冲突了", "两人改了同一行", "手动选要哪边，再 commit"],
  ["忘了起分支", "直接改了 main", "git stash → 起分支 → git stash pop"]
], {
  x: 0.6, y: 3.55, w: 8.8, h: 1.6,
  colW: [2.5, 3.0, 3.3],
  border: { pt: 0.5, color: "E2E8F0" },
  fontSize: 11,
  fontFace: "Arial",
  color: "334155",
  valign: "middle"
});

// ============================================
// 第 5.5 页 | 实用工具推荐：DevSidecar
// ============================================
let s5_5 = pres.addSlide();
s5_5.background = { color: WHITE };

s5_5.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s5_5.addText("实用工具推荐", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s5_5.addText("DevSidecar — 解决 GitHub 网络问题", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 问题描述框
s5_5.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.5, w: 8.8, h: 0.8,
  fill: { color: "FEF3C7" },
  line: { color: "F59E0B", width: 1 }
});
s5_5.addText("问题：git push / git clone 连不上 GitHub，报错 timeout", {
  x: 0.8, y: 1.6, w: 8.4, h: 0.6,
  fontSize: 12, color: "92400E", fontFace: "Arial", valign: "middle"
});

// 特点列表
s5_5.addText("特点", {
  x: 0.6, y: 2.5, w: 8.8, h: 0.35,
  fontSize: 14, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

s5_5.addText([
  { text: "• ", options: { color: NAVY } },
  { text: "桌面软件，Windows / Mac / Linux 都支持", options: { color: "334155" } },
  { text: "\n• ", options: { color: NAVY } },
  { text: "点击\"一键加速\"，系统全局生效", options: { color: "334155" } },
  { text: "\n• ", options: { color: NAVY } },
  { text: "命令行里的 git push 也能走加速通道", options: { color: "334155" } },
  { text: "\n• ", options: { color: NAVY } },
  { text: "同时还加速 npm、pip、Stack Overflow 等", options: { color: "334155" } }
], {
  x: 0.6, y: 2.9, w: 8.8, h: 1.8,
  fontSize: 12, fontFace: "Arial", lineSpacing: 22
});

// 适用场景
s5_5.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.8, w: 8.8, h: 0.6,
  fill: { color: LIGHT_BG },
  line: { color: ICE_BLUE, width: 1 }
});
s5_5.addText("适用：git clone 大型仓库、pip/npm install、GitHub Release 下载", {
  x: 0.8, y: 4.85, w: 8.4, h: 0.5,
  fontSize: 11, color: SLATE, fontFace: "Arial", valign: "middle"
});

// ============================================
// 第 6 页 | CC Usage（1/2）Token 是什么
// ============================================
let s6 = pres.addSlide();
s6.background = { color: WHITE };

s6.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s6.addText("CC Usage", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s6.addText("（1/2）Token 是什么，为什么要统计", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// Token 定义框
s6.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.5, w: 8.8, h: 1.6,
  fill: { color: LIGHT_BG },
  line: { color: ICE_BLUE, width: 1.5 }
});
s6.addText([
  { text: "Token = AI 模型的计费单位", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "· 不是字数，是模型处理文本时的最小单元", options: { color: "475569", breakLine: true } },
  { text: "· 英文约 1 token ≈ 0.75 个单词  |  中文约 1 token ≈ 0.5 个汉字", options: { color: "475569", breakLine: true } },
  { text: "· 输入和输出都计费", options: { color: "475569" } }
], { x: 0.8, y: 1.7, w: 8.4, h: 1.3, fontSize: 13, margin: 0 });

// 为什么要监控
s6.addText("为什么要监控", {
  x: 0.6, y: 3.4, w: 8.8, h: 0.3,
  fontSize: 14, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

const whyItems = [
  "LLM 调用按 token 计费，烧多了直接体现在账单上",
  "知道钱花在哪 = 知道时间花在哪",
  "发现异常消耗（死循环调用、重复请求）"
];
whyItems.forEach((item, i) => {
  s6.addShape(pres.shapes.OVAL, {
    x: 0.6, y: 3.85 + i * 0.45, w: 0.18, h: 0.18,
    fill: { color: NAVY }
  });
  s6.addText(String(i + 1), {
    x: 0.6, y: 3.85 + i * 0.45, w: 0.18, h: 0.18,
    fontSize: 9, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });
  s6.addText(item, {
    x: 0.9, y: 3.83 + i * 0.45, w: 8.5, h: 0.25,
    fontSize: 12, color: "475569", fontFace: "Arial", margin: 0
  });
});

// ============================================
// 第 7 页 | CC Usage（2/2）用法和省钱
// ============================================
let s7 = pres.addSlide();
s7.background = { color: WHITE };

s7.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s7.addText("CC Usage", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s7.addText("（2/2）用法和省钱技巧", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 左侧：安装和命令
s7.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.4, w: 4.5, h: 2.4,
  fill: { color: "1E293B" }
});
s7.addText([
  { text: "# 安装", options: { color: "64748B", breakLine: true } },
  { text: "npm install -g ccusage", options: { color: "A5B4FC", breakLine: true } },
  { text: "", options: { breakLine: true } },
  { text: "# 常用命令", options: { color: "64748B", breakLine: true } },
  { text: "ccusage today          # 今天", options: { color: "A5B4FC", breakLine: true } },
  { text: "ccusage week           # 本周", options: { color: "A5B4FC", breakLine: true } },
  { text: "ccusage by-model       # 按模型", options: { color: "A5B4FC", breakLine: true } },
  { text: "ccusage by-project     # 按项目", options: { color: "A5B4FC", breakLine: true } },
  { text: "ccusage export --csv   # 导出报表", options: { color: "A5B4FC" } }
], {
  x: 0.8, y: 1.55, w: 4.1, h: 2.1,
  fontSize: 10, fontFace: "Consolas", margin: 0
});

// 右侧：省钱技巧
s7.addText("省钱实操", {
  x: 5.4, y: 1.4, w: 4.0, h: 0.3,
  fontSize: 14, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});

const saveTips = [
  { head: "开发期用便宜模型", body: "GPT-4o-mini 调试，好了再上贵的" },
  { head: "上下文只放必要", body: "历史对话太长会累积计费" },
  { head: "批量处理", body: "批量比单条循环省 token" },
  { head: "定期看一眼", body: "ccusage week，异常早发现" }
];
saveTips.forEach((tip, i) => {
  const ty = 1.8 + i * 0.55;
  s7.addShape(pres.shapes.OVAL, {
    x: 5.4, y: ty, w: 0.3, h: 0.3,
    fill: { color: NAVY }
  });
  s7.addText(String(i + 1), {
    x: 5.4, y: ty, w: 0.3, h: 0.3,
    fontSize: 11, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });
  s7.addText(tip.head, {
    x: 5.85, y: ty, w: 3.5, h: 0.25,
    fontSize: 12, bold: true, color: NAVY, fontFace: "Arial", margin: 0
  });
  s7.addText(tip.body, {
    x: 5.85, y: ty + 0.25, w: 3.5, h: 0.25,
    fontSize: 11, color: "475569", fontFace: "Arial", margin: 0
  });
});

// ============================================
// 第 8 页 | AI 做 PPT（1/2）工作流
// ============================================
let s8 = pres.addSlide();
s8.background = { color: WHITE };

s8.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s8.addText("AI 辅助做 PPT", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s8.addText("（1/2）工作流对比", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 对比表格
s8.addTable([
  [
    { text: "步骤", options: { bold: true, fill: { color: NAVY }, color: WHITE, align: "center" } },
    { text: "传统做法", options: { bold: true, fill: { color: NAVY }, color: WHITE, align: "center" } },
    { text: "AI 辅助", options: { bold: true, fill: { color: NAVY }, color: WHITE, align: "center" } }
  ],
  ["写大纲", "自己想", "告诉 AI 主题 + 受众，生成大纲"],
  ["写内容", "逐页敲", "AI 按大纲扩写要点"],
  ["排版", "手动调", "Markdown / 文本 → 自动生成 PPT"],
  ["美化", "找模板", "AI 建议配色、配图"]
], {
  x: 0.6, y: 1.5, w: 8.8, h: 2.5,
  colW: [1.5, 3.5, 3.8],
  border: { pt: 0.5, color: "E2E8F0" },
  fontSize: 12,
  fontFace: "Arial",
  color: "334155",
  valign: "middle"
});

// 核心公式
s8.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.3, w: 8.8, h: 0.9,
  fill: { color: LIGHT_BG },
  line: { color: ICE_BLUE, width: 1.5 }
});
s8.addText([
  { text: "核心公式", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "给 AI 的指令 = 主题 + 受众 + 页数 + 风格 + 特殊要求", options: { color: "475569" } }
], { x: 0.8, y: 4.45, w: 8.4, h: 0.7, fontSize: 13, margin: 0 });

// ============================================
// 第 9 页 | AI 做 PPT（2/2）实操步骤
// ============================================
let s9 = pres.addSlide();
s9.background = { color: WHITE };

s9.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s9.addText("AI 辅助做 PPT", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s9.addText("（2/2）实操步骤", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

const pptSteps = [
  { step: "Step 1", title: "生成大纲", body: "给 AI 主题 + 受众 + 页数 + 风格\nAI 输出结构化的每页标题和要点" },
  { step: "Step 2", title: "扩写内容", body: "把大纲每页丢给 AI\n要求扩写成 bullet points" },
  { step: "Step 3", title: "生成 PPT 文件", body: "· Claude Code 的 pptx skill 直接生成 .pptx\n· 或在线工具（Gamma、Tome）导入 Markdown" },
  { step: "Step 4", title: "人工润色", body: "· AI 生成的是骨架，数据必须自己核对\n· 关键结论和数字，人工 double-check\n· 配色和字体按公司规范调整" }
];

pptSteps.forEach((s, i) => {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const cx = 0.6 + col * 4.5;
  const cy = 1.5 + row * 2.1;

  // 卡片背景
  s9.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: 4.3, h: 1.9,
    fill: { color: WHITE },
    line: { color: "E2E8F0", width: 1 },
    shadow: makeShadow()
  });

  // Step badge
  s9.addShape(pres.shapes.RECTANGLE, {
    x: cx + 0.2, y: cy + 0.15, w: 0.8, h: 0.28,
    fill: { color: NAVY }
  });
  s9.addText(s.step, {
    x: cx + 0.2, y: cy + 0.15, w: 0.8, h: 0.28,
    fontSize: 10, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });

  // 标题
  s9.addText(s.title, {
    x: cx + 1.1, y: cy + 0.15, w: 3.0, h: 0.3,
    fontSize: 14, bold: true, color: NAVY, fontFace: "Arial", margin: 0
  });

  // 内容
  s9.addText(s.body, {
    x: cx + 0.2, y: cy + 0.55, w: 3.9, h: 1.2,
    fontSize: 11, color: "475569", fontFace: "Arial",
    valign: "top", margin: 0
  });
});

// ============================================
// 第 10 页 | 快速上手清单
// ============================================
let s10 = pres.addSlide();
s10.background = { color: WHITE };

s10.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.15, h: 5.625,
  fill: { color: NAVY }
});

s10.addText("快速上手清单", {
  x: 0.6, y: 0.35, w: 8.8, h: 0.6,
  fontSize: 32, bold: true, color: NAVY, fontFace: "Arial", margin: 0
});
s10.addText("这周就能用起来的 3 件事", {
  x: 0.6, y: 0.9, w: 8.8, h: 0.35,
  fontSize: 14, color: SLATE, fontFace: "Arial", margin: 0
});

// 三件事
const threeThings = [
  { icon: "1", color: "0D9488", title: "Git", body: "把当前项目 init 了\n每天下班前 commit 一次" },
  { icon: "2", color: "2563EB", title: "CC Usage", body: "装完跑 ccusage today\n建立 baseline" },
  { icon: "3", color: "7C3AED", title: "PPT", body: "下次汇报前\n先用 AI 生成大纲" }
];

threeThings.forEach((t, i) => {
  const cx = 0.6 + i * 3.05;
  const cy = 1.5;

  // 卡片
  s10.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: 2.9, h: 2.2,
    fill: { color: LIGHT_BG },
    line: { color: "E2E8F0", width: 1 }
  });

  // 顶部色条
  s10.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cy, w: 2.9, h: 0.1,
    fill: { color: t.color }
  });

  // 图标圆圈
  s10.addShape(pres.shapes.OVAL, {
    x: cx + 1.05, y: cy + 0.3, w: 0.8, h: 0.8,
    fill: { color: t.color }
  });
  s10.addText(t.icon, {
    x: cx + 1.05, y: cy + 0.3, w: 0.8, h: 0.8,
    fontSize: 24, bold: true, color: WHITE,
    align: "center", valign: "middle", fontFace: "Arial", margin: 0
  });

  // 标题
  s10.addText(t.title, {
    x: cx, y: cy + 1.2, w: 2.9, h: 0.3,
    fontSize: 16, bold: true, color: NAVY,
    align: "center", fontFace: "Arial", margin: 0
  });

  // 内容
  s10.addText(t.body, {
    x: cx + 0.15, y: cy + 1.55, w: 2.6, h: 0.8,
    fontSize: 11, color: "475569",
    align: "center", fontFace: "Arial", margin: 0
  });
});

// 进阶路线
s10.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 4.0, w: 8.8, h: 1.3,
  fill: { color: WHITE },
  line: { color: "E2E8F0", width: 1 }
});
s10.addText([
  { text: "进阶路线", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "Week 1：熟练 Git 基础循环  →  Week 2：看懂 CC Usage 报告，优化 token 消耗  →  Week 3：独立用 AI 完成 PPT 从大纲到成品", options: { color: "475569" } }
], { x: 0.8, y: 4.15, w: 8.4, h: 1.0, fontSize: 12, margin: 0 });

// ============================================
// 第 11 页 | 结束页 (深色底)
// ============================================
let s11 = pres.addSlide();
s11.background = { color: NAVY };

// 装饰圆
s11.addShape(pres.shapes.OVAL, {
  x: 7.5, y: -1.5, w: 4, h: 4,
  fill: { color: ICE_BLUE, transparency: 85 }
});
s11.addShape(pres.shapes.OVAL, {
  x: -1.2, y: 3.8, w: 2.5, h: 2.5,
  fill: { color: ICE_BLUE, transparency: 90 }
});

// 主标题
s11.addText("开始用吧", {
  x: 0.8, y: 1.8, w: 8.4, h: 0.9,
  fontSize: 48, bold: true, color: WHITE, fontFace: "Arial",
  margin: 0
});

// 副标题
s11.addText("工欲善其事，必先利其器", {
  x: 0.8, y: 2.8, w: 8.4, h: 0.5,
  fontSize: 22, color: ICE_BLUE, fontFace: "Arial",
  margin: 0
});

// 底部
s11.addText("有问题随时问", {
  x: 0.8, y: 4.8, w: 8.4, h: 0.4,
  fontSize: 14, color: ICE_BLUE, fontFace: "Arial",
  margin: 0
});

// 底部分割线
s11.addShape(pres.shapes.RECTANGLE, {
  x: 0.8, y: 5.2, w: 2.5, h: 0.04,
  fill: { color: ICE_BLUE }
});

// ============================================
// 输出
// ============================================
pres.writeFile({ fileName: "20260520_AI工具指南.pptx" });
console.log("Generated: 20260520_AI工具指南.pptx");
