#!/usr/bin/env python3
"""从 drafts/*.md 生成可离线/手机浏览的 standalone.html"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path

PREVIEW = Path(__file__).resolve().parent
ROOT = PREVIEW.parent
DRAFTS = ROOT / "drafts"
OUT = PREVIEW / "standalone.html"

CHAPTERS = [
    ("drafts/prologue.md", "序章 · 错位的清晨"),
]


def chapter_anchor(label: str) -> str:
    """章节锚点 id，与 section 的 id 属性一致。"""
    return label.replace(" ", "-")


def discover_chapters() -> list[tuple[str, str]]:
    """按 prologue → chapter-NNN 顺序扫描 drafts/*.md（排除 README）。"""
    if CHAPTERS:
        return CHAPTERS
    items: list[tuple[str, str]] = []
    for path in sorted(DRAFTS.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        first = path.read_text(encoding="utf-8").split("\n", 1)[0].strip()
        label = first[2:].strip() if first.startswith("# ") else path.stem
        items.append((f"drafts/{path.name}", label))
    prologue = [x for x in items if "prologue" in x[0]]
    numbered = sorted(x for x in items if x not in prologue)
    return prologue + numbered


def md_to_html(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    in_para = False
    in_setting = False
    setting_para_open = False
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if line.strip() == "【附】":
            if in_para:
                out.append("</p>")
                in_para = False
            in_setting = True
            setting_para_open = False
            out.append('<aside class="setting-note">')
            i += 1
            continue

        if line.strip() == "【/附】":
            if in_setting and setting_para_open:
                out.append("</p>")
                setting_para_open = False
            if in_setting:
                out.append("</aside>")
                in_setting = False
            i += 1
            continue

        if in_setting:
            if not line.strip():
                if setting_para_open:
                    out.append("</p>")
                    setting_para_open = False
            else:
                if not setting_para_open:
                    cls = ' class="setting-label"' if line.strip().startswith("附：") else ""
                    out.append(f"<p{cls}>")
                    setting_para_open = True
                else:
                    out.append("<br/>")
                out.append(html.escape(line))
            i += 1
            continue

        if line.startswith("# "):
            if in_para:
                out.append("</p>")
                in_para = False
            out.append(f"<h2>{html.escape(line[2:])}</h2>")
            i += 1
            continue
        if line in ("*", "---"):
            if in_para:
                out.append("</p>")
                in_para = False
            out.append('<hr class="scene" />')
            i += 1
            continue
        if not line.strip():
            if in_para:
                out.append("</p>")
                in_para = False
            i += 1
            continue
        if not in_para:
            no_indent = line.strip().startswith("「") or line.strip().startswith("觉醒前")
            cls = ' class="no-indent"' if no_indent else ""
            out.append(f"<p{cls}>")
            in_para = True
        else:
            out.append("<br/>")
        out.append(html.escape(line))
        i += 1

    if in_para:
        out.append("</p>")
    if in_setting:
        if setting_para_open:
            out.append("</p>")
        out.append("</aside>")
    return "".join(out)


def build_toc(chapters: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f'      <li><a href="#{html.escape(chapter_anchor(label), quote=True)}">{html.escape(label)}</a></li>'
        for _, label in chapters
    )
    return f"""  <nav class="toc" aria-label="目录">
    <details class="toc-panel" open>
      <summary class="toc-summary">目录</summary>
      <ol class="toc-list">
{items}
      </ol>
    </details>
  </nav>"""


def main() -> None:
    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    chapters = discover_chapters()
    sections = []
    for rel, label in chapters:
        path = ROOT / rel.replace("drafts/", "drafts/")
        md = path.read_text(encoding="utf-8")
        anchor = chapter_anchor(label)
        sections.append((label, anchor, md_to_html(md)))

    toc = build_toc(chapters)
    body = "\n".join(
        f'<section id="{html.escape(anchor)}" class="chapter-section">'
        f'<h2 class="chapter">{html.escape(label)}</h2>{content}</section>'
        for label, anchor, content in sections
    )

    title_suffix = " · ".join(label.split(" · ", 1)[0] for _, label in chapters[:3])
    if len(chapters) > 3:
        title_suffix += "…"

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
  <meta http-equiv="refresh" content="300" />
  <title>小说正文预览 · {html.escape(title_suffix)}</title>
  <style>
    :root {{
      --bg: #faf8f5; --text: #2c2825; --muted: #7a7268;
      --card: #fff; --border: #e8e2d9; --scene: #c4b8a8; --accent: #8b6914;
      --toc-width: 13.5rem;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #1a1816; --text: #ebe6df; --muted: #9a9288;
        --card: #242120; --border: #3a3530; --scene: #5a5248; --accent: #d4b86a;
      }}
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0; font-family: "PingFang SC", "Noto Serif SC", serif;
      background: var(--bg); color: var(--text);
      line-height: 1.85; font-size: 18px;
    }}
    header {{
      position: sticky; top: 0; z-index: 20;
      background: var(--card); border-bottom: 1px solid var(--border);
      padding: 14px 16px; box-shadow: 0 1px 8px rgba(0,0,0,.06);
    }}
    header h1 {{ margin: 0 0 6px; font-size: 1.1rem; }}
    .meta {{ font-size: .78rem; color: var(--muted); }}
    .layout {{
      display: flex; align-items: flex-start;
      max-width: 56rem; margin: 0 auto;
      padding: 0 12px 48px; gap: 0;
    }}
    .toc {{
      flex: 0 0 var(--toc-width);
      position: sticky; top: 4.5rem;
      align-self: flex-start;
      padding: 16px 8px 16px 4px;
      max-height: calc(100vh - 5rem);
      overflow-y: auto;
    }}
    .toc-panel {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0;
      margin: 0;
    }}
    .toc-summary {{
      list-style: none;
      cursor: pointer;
      font-size: .92rem;
      font-weight: 600;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      user-select: none;
    }}
    .toc-summary::-webkit-details-marker {{ display: none; }}
    .toc-summary::before {{
      content: "▾ "; color: var(--accent); font-size: .85em;
    }}
    .toc-panel:not([open]) .toc-summary::before {{ content: "▸ "; }}
    .toc-list {{
      margin: 0; padding: 8px 0 10px;
      list-style: none;
      counter-reset: toc;
    }}
    .toc-list li {{
      counter-increment: toc;
      margin: 0;
    }}
    .toc-list a {{
      display: block;
      padding: 7px 12px 7px 10px;
      font-size: .86rem;
      line-height: 1.45;
      color: var(--text);
      text-decoration: none;
      border-left: 3px solid transparent;
    }}
    .toc-list a:hover,
    .toc-list a:focus {{
      background: var(--border);
      border-left-color: var(--accent);
      outline: none;
    }}
    main {{
      flex: 1; min-width: 0;
      max-width: 42rem;
      padding: 16px 6px 0;
    }}
    section.chapter-section {{ margin-bottom: 2.5em; scroll-margin-top: 5rem; }}
    h2.chapter {{ font-size: 1.25rem; text-align: center; margin: 0 0 1em; }}
    article p {{ margin: 0 0 1.1em; text-indent: 2em; text-align: justify; }}
    article p.no-indent {{ text-indent: 0; }}
    aside.setting-note {{
      margin: 0.6em 0 1.2em; padding: 10px 14px;
      background: var(--border); border-left: 3px solid var(--accent);
      font-size: 0.88rem; line-height: 1.7; color: var(--muted);
    }}
    aside.setting-note p {{ text-indent: 0; margin: 0 0 0.5em; }}
    aside.setting-note p.setting-label {{ font-weight: 600; color: var(--text); margin-bottom: 0.6em; }}
    aside.setting-note p:last-child {{ margin-bottom: 0; }}
    hr.scene {{ border: none; text-align: center; margin: 1.6em 0; color: var(--scene); letter-spacing: .5em; }}
    hr.scene::before {{ content: "· · ·"; }}
    footer {{
      text-align: center; font-size: .75rem; color: var(--muted);
      padding: 16px; max-width: 56rem; margin: 0 auto;
    }}
    @media (max-width: 720px) {{
      .layout {{ display: block; padding: 0 0 48px; }}
      .toc {{
        position: sticky; top: 3.8rem; z-index: 15;
        flex: none; width: 100%; max-height: none;
        padding: 0; background: var(--bg);
        border-bottom: 1px solid var(--border);
      }}
      .toc-panel {{ border: none; border-radius: 0; }}
      .toc-panel:not([open]) .toc-list {{ display: none; }}
      main {{ padding: 16px 18px 0; max-width: none; }}
    }}
    @media (min-width: 721px) {{
      .toc-panel {{ pointer-events: none; }}
      .toc-summary {{ pointer-events: none; cursor: default; }}
      .toc-list a {{ pointer-events: auto; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>异世界重生 · 正文预览</h1>
    <div class="meta">构建于 {built} · 每 300 秒自动刷新页面以同步最新稿</div>
  </header>
  <div class="layout">
{toc}
    <main><article>{body}</article></main>
  </div>
  <footer>手机阅读：下拉刷新或等待自动刷新（5 分钟）· 改稿推送后更新</footer>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} ({built}) · {len(chapters)} 章")


if __name__ == "__main__":
    main()
