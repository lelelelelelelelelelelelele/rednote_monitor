# Report 管理规范

> 本规范用于统一项目汇报材料的生成、存放和版本管理。
> AI 生成痕迹不隐藏，保留完整上下文。
>
> **支持两种产出格式：PPT（演示场景）和 HTML（长文档场景），任选其一。** 详见下文"输出格式"一节。

---

## 目录结构

```
report/
├── RULES.md                          # 本文件
├── YYYYMMDD/                         # 日期层（时间聚合）
│   └── {人}_{主题}/                   # 每次汇报独立一盒
│       ├── outline.md                # 文字大纲（源文件，PPT/HTML 共用）
│       ├── outline.v{数字}.md        # 大纲历史版本
│       ├── gen.js                    # 生成脚本（PPT 用 pptxgenjs / HTML 用 markdown-it）
│       ├── {YYYYMMDD}_{主题}.pptx    # 输出（PPT 路线）
│       ├── {YYYYMMDD}_{主题}.html    # 输出（HTML 路线，单文件自包含）
│       └── package.json              # 脚本依赖
├── scripts/                          # 公共脚本（PPT 转 PDF 等）
└── .gitignore                        # 忽略 *.pdf + node_modules/
```

---

## 核心规则

### 1. 同文件夹原则

**大纲、PPT 源文件、生成脚本必须放在同一个子目录下。**

```
report/20260520/lele_启动会/
  ├── outline.md          ← 文字版（人可读、可改）
  ├── gen.js              ← 生成脚本（AI 可执行）
  └── 20260520_启动会.pptx ← 输出文件
```

### 2. 修改同步原则

**改大纲 → 同步改 PPT → 同步改 PDF。**

顺序：
1. 先改 `outline.md`
2. 同步更新 `gen.js` 里的对应内容
3. 运行 `node gen.js` 重新生成 PPT
4. 运行 `node gen.js --pdf` 或手动转 PDF

禁止：只改 PPT 不改大纲，导致两者分叉。

### 3. 版本命名

大纲修改时保留历史版本：

```
outline.md           ← 当前版本
outline.v1.md        ← 第一次修改前
outline.v2.md        ← 第二次修改前
```

PPT 文件名始终用日期 + 主题，不附加版本号。

### 4. AI 痕迹不隐藏

- 生成脚本（gen.js）保留完整代码，不压缩、不混淆
- 如使用 AI 辅助生成，commit message 如实写 "AI-generated: ..."
- 不删除生成脚本里的注释和调试日志

### 5. PDF / 截图输出

每次生成 PPT 后，**本地生成 PDF 或逐页截图**，方便没有 PowerPoint 的人查看。

**PDF 不入 git**（`report/.gitignore` 已忽略 `*.pdf`），需要时从 PPTX 重新生成。

方式 A（PowerPoint COM，Windows）：
```powershell
# convert-to-pdf.ps1
$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open("$PWD\xxx.pptx")
$pres.SaveAs("$PWD\xxx.pdf", 32)
$pres.Close()
$ppt.Quit()
```

方式 B（LibreOffice headless）：
```bash
soffice --headless --convert-to pdf xxx.pptx
```

方式 C（逐页截图，需要 pdftoppm）：
```bash
soffice --headless --convert-to pdf xxx.pptx
pdftoppm -jpeg -r 150 xxx.pdf slide
```

---

## 输出格式

### PPT 路线（演示导向）

- 用 `pptxgenjs` 在 `gen.js` 里搭页。一页一页讲，适合开会过场。
- 输出 `{YYYYMMDD}_{主题}.pptx`，本地转 PDF 给没装 Office 的人看。
- 已沉淀模板：`report/20260520/lele_启动会/`。

### HTML 路线（文档导向）

- 用 `markdown-it`（或类似）在 `gen.js` 里把 `outline.md` → 单文件 HTML（CSS 内联，不依赖外部 CDN）。
- 输出 `{YYYYMMDD}_{主题}.html`，浏览器双击打开即可看。
- 适合：技术细节多、要嵌代码块/PR 链接/截图、要求"既能上传也能直接读"的场景。
- 优势：与 `outline.md` 几乎 1:1 对应，改 md 跑一次 `node gen.js` 即可，不像 PPT 要手工同步两边。
- 演示方式：浏览器开全屏 + 顶部 TOC 锚点跳转，配合 `Ctrl + F` 比翻页快。
- 已沉淀模板：`report/20260527/lele_Week2进展/`。

### 怎么选

| 场景 | 选 |
|---|---|
| 启动会 / 对外分享 / 强视觉演示 | PPT |
| 周报 / 技术进展 / 嵌代码和链接多 | HTML |
| 想给 AI / 同学直接读 md 也行 | 两种都把 `outline.md` 留全 |

不强求统一，作者按内容性质决定。**outline.md 始终是源文件**，这条不变。

---

## 快速开始

```powershell
cd E:\project\rednote_monitor\report

# 1. 新建一期汇报（日期层 + 人_主题）
mkdir -p 20260520\lele_启动会
cd 20260520\lele_启动会

# 2. 写 outline.md（先写文字大纲）
# ...

# 3. 写 gen.js（AI 根据大纲生成 PPT 脚本）
# ...

# 4. 生成 PPT
npm install pptxgenjs
node gen.js

# 5. 生成 PDF（本地查看用，不入 git）
.\..\..\scripts\convert-pptx-to-pdf.ps1 20260520_启动会.pptx
```

### HTML 路线的快速开始

```powershell
cd E:\project\rednote_monitor\report
mkdir -p 20260527\lele_Week2进展
cd 20260527\lele_Week2进展

# 1. 写 outline.md
# 2. 写 gen.js（markdown-it 转 HTML，CSS 内联）
npm install markdown-it
node gen.js
# 输出 20260527_Week2进展.html，浏览器打开
```
