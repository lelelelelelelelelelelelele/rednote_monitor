# Report 管理规范

> 本规范用于统一项目汇报材料的生成、存放和版本管理。
> AI 生成痕迹不隐藏，保留完整上下文。

---

## 目录结构

```
report/
├── RULES.md                          # 本文件
├── YYYYMMDD/                         # 日期层（时间聚合）
│   └── {人}_{主题}/                   # 每次汇报独立一盒
│       ├── outline.md                # 文字大纲（源文件）
│       ├── outline.v{数字}.md        # 大纲历史版本
│       ├── gen.js                    # PPT 生成脚本（Node + pptxgenjs）
│       ├── {YYYYMMDD}_{主题}.pptx    # PPT 源文件
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
