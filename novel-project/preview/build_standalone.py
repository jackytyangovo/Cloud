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


def main() -> None:
    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections = []
    for rel, label in CHAPTERS:
        path = ROOT / rel.replace("drafts/", "drafts/")
        md = path.read_text(encoding="utf-8")
        sections.append((label, md_to_html(md)))

    body = "\n".join(
        f'<section id="{html.escape(label)}"><h2 class="chapter">{html.escape(label)}</h2>{content}</section>'
        for label, content in sections
    )

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
  <meta http-equiv="refresh" content="300" />
  <title>小说正文预览 · 序章</title>
  <style>
    :root {{
      --bg: #faf8f5; --text: #2c2825; --muted: #7a7268;
      --card: #fff; --border: #e8e2d9; --scene: #c4b8a8; --accent: #8b6914;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #1a1816; --text: #ebe6df; --muted: #9a9288;
        --card: #242120; --border: #3a3530; --scene: #5a5248; --accent: #d4b86a;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: "PingFang SC", "Noto Serif SC", serif;
      background: var(--bg); color: var(--text);
      line-height: 1.85; font-size: 18px;
    }}
    header {{
      position: sticky; top: 0; z-index: 10;
      background: var(--card); border-bottom: 1px solid var(--border);
      padding: 14px 16px; box-shadow: 0 1px 8px rgba(0,0,0,.06);
    }}
    header h1 {{ margin: 0 0 6px; font-size: 1.1rem; }}
    .meta {{ font-size: .78rem; color: var(--muted); }}
    main {{ max-width: 42rem; margin: 0 auto; padding: 20px 18px 48px; }}
    section {{ margin-bottom: 2.5em; }}
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
    footer {{ text-align: center; font-size: .75rem; color: var(--muted); padding: 16px; }}
  </style>
</head>
<body>
  <header>
    <h1>异世界重生 · 正文预览</h1>
    <div class="meta">构建于 {built} · 每 300 秒自动刷新页面以同步最新稿</div>
  </header>
  <main><article>{body}</article></main>
  <footer>手机阅读：下拉刷新或等待自动刷新（5 分钟）· 改稿推送后更新</footer>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} ({built})")


if __name__ == "__main__":
    main()
