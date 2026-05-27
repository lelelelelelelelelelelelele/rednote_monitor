// gen.js — outline.md → 20260527_w2.html
//
// 用法：
//   npm install
//   node gen.js
//
// 输入：outline.md（同目录）
// 输出：20260527_w2.html（同目录，单文件自包含，CSS 内联）
//
// 设计：
// - 长滚动文档（不是幻灯片）。左侧 sticky TOC，右侧正文。窄屏自动堆叠。
// - 配色对齐启动会 PPT 的 Midnight Executive（navy #1E2761）。
// - 自动从 h2 / h3 抽 TOC，给每个 heading 加 id（slug）锚点。

const fs = require('fs');
const path = require('path');
const MarkdownIt = require('markdown-it');

// linkify: false —— outline.md 里 CLAUDE.md / xxx.py 这类裸文件名会被误识别为域名。
// 真正的链接都用 [text](url) 显式写。
const md = new MarkdownIt({
  html: true,
  linkify: false,
  typographer: true,
  breaks: false,
});

// ---- 自动给 h2 / h3 加 id + 收集 TOC ----
function slugify(s) {
  return s
    .toLowerCase()
    .trim()
    .replace(/[　\s]+/g, '-')
    .replace(/[^\w一-龥-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

const toc = [];
md.core.ruler.push('collect_toc', (state) => {
  const used = new Map();
  for (let i = 0; i < state.tokens.length; i++) {
    const t = state.tokens[i];
    if (t.type !== 'heading_open') continue;
    if (t.tag !== 'h2' && t.tag !== 'h3') continue;
    const inline = state.tokens[i + 1];
    const text = inline ? inline.content : '';
    let id = slugify(text);
    // 重复 id 加后缀
    if (used.has(id)) {
      const n = used.get(id) + 1;
      used.set(id, n);
      id = `${id}-${n}`;
    } else {
      used.set(id, 0);
    }
    t.attrSet('id', id);
    toc.push({ level: t.tag, text, id });
  }
});

const srcPath = path.join(__dirname, 'outline.md');
const outPath = path.join(__dirname, '20260527_w2.html');

const src = fs.readFileSync(srcPath, 'utf8');
const body = md.render(src);

const tocHtml = toc
  .map((item) => {
    const cls = item.level === 'h3' ? 'toc-sub' : 'toc-main';
    return `<li class="${cls}"><a href="#${item.id}">${escapeHtml(item.text)}</a></li>`;
  })
  .join('\n        ');

function escapeHtml(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ---- HTML 模板 ----
const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>M1 v2 准备 · w2（lele）</title>
<style>
:root {
  --navy: #1E2761;
  --navy-light: #2d3a8c;
  --ice: #7ED4E6;
  --text: #1f2937;
  --text-mute: #6b7280;
  --bg: #ffffff;
  --bg-soft: #f6f8fa;
  --bg-toc: #f9fafb;
  --border: #e5e7eb;
  --accent: #1E2761;
  --code-bg: #f6f8fa;
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; scroll-padding-top: 2rem; }

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  font-size: 16px;
  line-height: 1.75;
  color: var(--text);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
}

.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  max-width: 1280px;
  margin: 0 auto;
  gap: 2rem;
  padding: 2rem 2rem 4rem;
}

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; padding: 1rem; }
  .toc { position: static !important; max-height: none !important; }
  .content table { display: block; overflow-x: auto; }
}

/* ===== TOC ===== */
.toc {
  position: sticky;
  top: 1rem;
  align-self: start;
  max-height: calc(100vh - 2rem);
  overflow-y: auto;
  background: var(--bg-toc);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.25rem 1rem;
  font-size: 0.875rem;
}

.toc h4 {
  margin: 0 0 0.75rem 0;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-mute);
  font-weight: 600;
}

.toc ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc li { margin: 0.25rem 0; }
.toc li.toc-sub { padding-left: 1rem; font-size: 0.8125rem; }

.toc a {
  color: var(--text);
  text-decoration: none;
  display: block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border-left: 2px solid transparent;
}

.toc a:hover {
  background: #fff;
  border-left-color: var(--accent);
  color: var(--accent);
}

/* ===== Content ===== */
.content {
  min-width: 0; /* 防止 grid overflow */
  max-width: 820px;
}

.content h1 {
  font-size: 2rem;
  margin: 0 0 0.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 3px solid var(--navy);
  color: var(--navy);
  font-weight: 700;
}

.content h2 {
  font-size: 1.5rem;
  margin: 2.5rem 0 1rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border);
  color: var(--navy);
  font-weight: 600;
}

.content h3 {
  font-size: 1.15rem;
  margin: 1.75rem 0 0.75rem;
  color: var(--navy-light);
  font-weight: 600;
}

.content h4 {
  font-size: 1rem;
  margin: 1.25rem 0 0.5rem;
  color: var(--text);
  font-weight: 600;
}

.content p { margin: 0.75rem 0; }

.content a { color: var(--accent); text-decoration: none; }
.content a:hover { text-decoration: underline; }

/* blockquote */
.content blockquote {
  margin: 1rem 0;
  padding: 0.75rem 1rem;
  background: var(--bg-soft);
  border-left: 3px solid var(--navy);
  color: var(--text);
  border-radius: 0 6px 6px 0;
}
.content blockquote p { margin: 0.3rem 0; }
.content blockquote strong { color: var(--text); }

/* tables */
.content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.95rem;
}

.content table thead {
  background: var(--navy);
  color: #fff;
}

.content table th,
.content table td {
  padding: 0.5rem 0.75rem;
  text-align: left;
  border: 1px solid var(--border);
  vertical-align: top;
}

.content table tbody tr:nth-child(even) {
  background: var(--bg-soft);
}

/* code */
.content code {
  font-family: "JetBrains Mono", "Fira Code", Consolas, "Liberation Mono",
    Menlo, Courier, monospace;
  font-size: 0.875em;
  background: var(--code-bg);
  padding: 0.15em 0.4em;
  border-radius: 4px;
  color: var(--navy-light);
}

.content pre {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  font-size: 0.875rem;
  line-height: 1.55;
}

.content pre code {
  background: transparent;
  padding: 0;
  color: var(--text);
  font-size: inherit;
}

/* lists */
.content ul, .content ol { padding-left: 1.5rem; }
.content li { margin: 0.25rem 0; }
.content li > ul, .content li > ol { margin: 0.25rem 0; }

/* hr */
.content hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2rem 0;
}

/* checklist (- [ ] / - [x]) */
.content li input[type="checkbox"] {
  margin-right: 0.4rem;
}

/* 强调小红点（自定义状态徽章） */
.content em { color: var(--text-mute); font-style: italic; }
.content strong { color: var(--text); }

/* print */
@media print {
  .layout { display: block; padding: 1rem; }
  .toc { display: none; }
  .content { max-width: 100%; }
  .content a { color: var(--text); }
}

footer.meta {
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  font-size: 0.8125rem;
  color: var(--text-mute);
  text-align: center;
}
</style>
</head>
<body>
<div class="layout">
  <aside class="toc">
    <h4>目录</h4>
    <ul>
        ${tocHtml}
    </ul>
  </aside>
  <main class="content">
${body}
    <footer class="meta">
      生成于 ${new Date().toISOString().slice(0, 10)} · markdown-it + 内联 CSS · 单文件可上传
    </footer>
  </main>
</div>
</body>
</html>
`;

fs.writeFileSync(outPath, html, 'utf8');
console.log(`✓ Generated ${path.basename(outPath)} (${(html.length / 1024).toFixed(1)} KB)`);
console.log(`  TOC entries: ${toc.length}`);
