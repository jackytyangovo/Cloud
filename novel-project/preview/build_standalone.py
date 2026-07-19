#!/usr/bin/env python3
"""生成可离线/手机浏览的 standalone.html。

同步规则（✓ 用户确认）：
- 有定稿 → 收录 finalized/
- 无定稿、仅有初稿 → 收录 drafts/
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PREVIEW = Path(__file__).resolve().parent
ROOT = PREVIEW.parent
DRAFTS = ROOT / "drafts"
FINALIZED = ROOT / "finalized"
OUT = PREVIEW / "standalone.html"
CONFIG_PATH = PREVIEW / "preview-config.json"
DEFAULT_CONFIG = {
    "github_repo": "jackytyangovo/Cloud",
    # 手机书签用的稳定分支（Actions 会把最新 standalone 同步到这里）
    "preview_branch": "preview",
    # 定时从哪条分支取正文重建（小说主工作分支）
    "source_branch": "cursor/style-check-prologue-129b",
    "refresh_interval_minutes": 1,
    "htmlpreview_base": "https://htmlpreview.github.io/?",
}

CHAPTER_NAME_RE = re.compile(r"^(prologue|chapter-\d+)\.md$", re.IGNORECASE)


def chapter_anchor(label: str) -> str:
    """章节锚点 id，与 section 的 id 属性一致。"""
    return label.replace(" ", "-")


def chapter_sort_key(name: str) -> tuple:
    lower = name.lower()
    if lower == "prologue.md":
        return (0, 0)
    m = re.match(r"chapter-(\d+)\.md$", lower)
    if m:
        return (1, int(m.group(1)))
    return (2, lower)


def resolve_chapter_path(filename: str) -> Path | None:
    """定稿优先；无定稿则用初稿。"""
    fin = FINALIZED / filename
    if fin.is_file():
        return fin
    draft = DRAFTS / filename
    if draft.is_file():
        return draft
    return None


def label_from_md(path: Path) -> str:
    first = path.read_text(encoding="utf-8").split("\n", 1)[0].strip()
    return first[2:].strip() if first.startswith("# ") else path.stem


def discover_chapters() -> list[tuple[str, str]]:
    """扫描 finalized/ + drafts/，按 prologue → chapter-NNN 排序。

    返回 (相对 novel-project 的路径, 章名标签每章优先 finalized。
    """
    names: set[str] = set()
    for folder in (FINALIZED, DRAFTS):
        if not folder.is_dir():
            continue
        for path in folder.glob("*.md"):
            if path.name.lower() == "readme.md":
                continue
            if CHAPTER_NAME_RE.match(path.name):
                names.add(path.name)

    items: list[tuple[str, str]] = []
    for name in sorted(names, key=chapter_sort_key):
        path = resolve_chapter_path(name)
        if path is None:
            continue
        rel = f"{path.parent.name}/{path.name}"
        items.append((rel, label_from_md(path)))
    return items


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
            # 仅章首日期顶格；对话/叙述均 text-indent，段首第一字对齐
            no_indent = line.strip().startswith("觉醒前")
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
        f'        <li><a href="#{html.escape(chapter_anchor(label), quote=True)}">{html.escape(label)}</a></li>'
        for _, label in chapters
    )
    return f"""  <button type="button" class="toc-toggle" id="toc-toggle" aria-expanded="false" aria-controls="toc-drawer">目录</button>
  <div class="toc-backdrop" id="toc-backdrop" hidden></div>
  <nav class="toc-drawer" id="toc-drawer" aria-label="目录" hidden>
    <div class="toc-header">
      <span class="toc-title">目录</span>
      <button type="button" class="toc-close" id="toc-close" aria-label="关闭目录">×</button>
    </div>
    <ol class="toc-list">
{items}
    </ol>
  </nav>"""


def load_preview_config() -> dict:
    if CONFIG_PATH.is_file():
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return {**DEFAULT_CONFIG, **data}
    return dict(DEFAULT_CONFIG)


def drafts_content_hash(chapters: list[tuple[str, str]]) -> str:
    """正文指纹：按实际收录文件（定稿或初稿）计算。"""
    h = hashlib.sha256()
    for rel, _ in chapters:
        path = ROOT / rel
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()[:12]


def read_embedded_drafts_sha(html_text: str) -> str | None:
    m = re.search(r'<meta name="drafts-sha" content="([^"]+)"', html_text)
    return m.group(1) if m else None


def read_embedded_preview_revision(html_text: str) -> str | None:
    m = re.search(r'<meta name="preview-revision" content="([^"]+)"', html_text)
    return m.group(1) if m else None


def read_embedded_build_script_sha(html_text: str) -> str | None:
    m = re.search(r'<meta name="build-script-sha" content="([^"]+)"', html_text)
    return m.group(1) if m else None


def build_script_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]


def preview_revision(page: str) -> str:
    """全文指纹：正文或预览模板任一变动都会变，供页内同步检测。"""
    return hashlib.sha256(page.encode("utf-8")).hexdigest()[:16]


def git_branch() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=ROOT.parent,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except Exception:
        return load_preview_config()["preview_branch"]


def git_short_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT.parent,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except Exception:
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build standalone.html（定稿优先，无定稿用初稿）"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild even when content hash is unchanged",
    )
    args = parser.parse_args()

    config = load_preview_config()
    refresh_min = int(config.get("refresh_interval_minutes", 5))
    refresh_ms = refresh_min * 60 * 1000

    chapters = discover_chapters()
    drafts_sha = drafts_content_hash(chapters)

    script_sha = build_script_hash()

    if OUT.is_file() and not args.force:
        existing = OUT.read_text(encoding="utf-8")
        if (
            read_embedded_drafts_sha(existing) == drafts_sha
            and read_embedded_preview_revision(existing) is not None
            and read_embedded_build_script_sha(existing) == script_sha
        ):
            print(
                f"Preview up to date (content {drafts_sha}, script {script_sha}), "
                "skip rebuild. Use --force to refresh."
            )
            return

    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sha = git_short_sha()
    branch = git_branch()
    repo = config["github_repo"]
    preview_branch = config.get("preview_branch") or branch
    raw_path = "/novel-project/preview/standalone.html"
    raw_url = (
        f"https://raw.githubusercontent.com/{repo}/{preview_branch}{raw_path}"
    )
    viewer_base = config.get("htmlpreview_base", DEFAULT_CONFIG["htmlpreview_base"])
    viewer_url = f"{viewer_base}{raw_url}"
    sections = []
    sources: list[str] = []
    for rel, label in chapters:
        path = ROOT / rel
        md = path.read_text(encoding="utf-8")
        anchor = chapter_anchor(label)
        sections.append((label, anchor, md_to_html(md)))
        sources.append(f"{label.split(' · ', 1)[0]}←{rel.split('/', 1)[0]}")

    toc = build_toc(chapters)
    body = "\n".join(
        f'<section id="{html.escape(anchor)}" class="chapter-section">'
        f'<h2 class="chapter">{html.escape(label)}</h2>{content}</section>'
        for label, anchor, content in sections
    )

    title_suffix = " · ".join(label.split(" · ", 1)[0] for _, label in chapters[:3])
    if len(chapters) > 3:
        title_suffix += "…"

    # 占位 revision，写入后再回填（revision 依赖完整 HTML）
    revision_placeholder = "__PREVIEW_REVISION__"

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta name="drafts-sha" content="{drafts_sha}" />
  <meta name="preview-revision" content="{revision_placeholder}" />
  <meta name="build-script-sha" content="{script_sha}" />
  <meta name="build-commit" content="{sha}" />
  <meta name="built-at" content="{built}" />
  <meta name="preview-raw-url" content="{html.escape(raw_url, quote=True)}" />
  <meta name="preview-viewer-url" content="{html.escape(viewer_url, quote=True)}" />
  <title>小说正文预览 · {html.escape(title_suffix)}</title>
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
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0; font-family: "PingFang SC", "Noto Serif SC", serif;
      background: var(--bg); color: var(--text);
      line-height: 1.85; font-size: 18px;
    }}
    header {{
      position: sticky; top: 0; z-index: 20;
      background: var(--card); border-bottom: 1px solid var(--border);
      box-shadow: 0 1px 6px rgba(0,0,0,.05);
    }}
    .header-bar {{
      display: flex; align-items: center; gap: 8px;
      padding: 6px 10px 6px 12px; min-height: 2.4rem;
    }}
    header h1 {{
      margin: 0; flex: 1; min-width: 0;
      font-size: .92rem; font-weight: 600;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .header-actions {{
      display: flex; align-items: center; gap: 6px; flex-shrink: 0;
    }}
    .header-chip {{
      border: 1px solid var(--border); background: var(--bg);
      color: var(--text); border-radius: 999px;
      padding: 3px 10px; font: inherit; font-size: .72rem;
      cursor: pointer; line-height: 1.3;
    }}
    .header-chip:hover, .header-chip:focus {{
      border-color: var(--accent); outline: none;
    }}
    .header-chip:disabled {{ opacity: .55; cursor: wait; }}
    .header-rev {{ cursor: default; opacity: .85; font-variant-numeric: tabular-nums; }}
    .header-rev:hover, .header-rev:focus {{ border-color: var(--border); }}
    .header-hint a {{ color: var(--accent); }}
    .header-panel {{
      display: none;
      padding: 0 12px 10px;
      border-top: 1px solid var(--border);
    }}
    header.is-expanded .header-panel {{ display: block; }}
    header.is-expanded .header-toggle {{ border-color: var(--accent); }}
    .meta {{ font-size: .72rem; color: var(--muted); margin: 8px 0 0; line-height: 1.45; }}
    .toc-toggle {{
      position: fixed; bottom: 18px; right: 16px; z-index: 30;
      padding: 8px 14px; border: 1px solid var(--border);
      border-radius: 999px; background: var(--card);
      color: var(--text); font: inherit; font-size: .82rem;
      cursor: pointer; box-shadow: 0 2px 10px rgba(0,0,0,.08);
    }}
    .toc-toggle:hover, .toc-toggle:focus {{
      border-color: var(--accent); outline: none;
    }}
    .toc-backdrop {{
      position: fixed; inset: 0; z-index: 40;
      background: rgba(0,0,0,.35);
    }}
    .toc-drawer {{
      position: fixed; top: 0; right: 0; z-index: 50;
      width: min(18rem, 88vw); height: 100%;
      background: var(--card); border-left: 1px solid var(--border);
      box-shadow: -4px 0 24px rgba(0,0,0,.12);
      display: flex; flex-direction: column;
      transform: translateX(100%);
      transition: transform .22s ease;
    }}
    .toc-drawer.is-open {{ transform: translateX(0); }}
    .toc-header {{
      display: flex; align-items: center; justify-content: space-between;
      padding: 14px 14px 10px; border-bottom: 1px solid var(--border);
      flex-shrink: 0;
    }}
    .toc-title {{ font-size: .95rem; font-weight: 600; }}
    .toc-close {{
      border: none; background: transparent; color: var(--muted);
      font-size: 1.4rem; line-height: 1; cursor: pointer; padding: 0 4px;
    }}
    .toc-close:hover, .toc-close:focus {{ color: var(--text); outline: none; }}
    .toc-list {{
      margin: 0; padding: 8px 0 16px;
      list-style: none; overflow-y: auto; flex: 1;
    }}
    .toc-list li {{ margin: 0; }}
    .toc-list a {{
      display: block;
      padding: 10px 16px;
      font-size: .88rem;
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
      max-width: 42rem; margin: 0 auto;
      padding: 16px 18px 48px;
    }}
    section.chapter-section {{ margin-bottom: 2.5em; scroll-margin-top: 3.2rem; }}
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
    footer {{ display: none; }}
    .preview-toolbar {{
      display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
      margin-top: 8px;
    }}
    .preview-sync-status {{ font-size: .72rem; color: var(--muted); }}
    .preview-sync-status.is-new {{ color: var(--accent); font-weight: 600; }}
    .preview-sync-status.is-err {{ color: #b42318; }}
    .header-hint {{
      margin: 6px 0 0; font-size: .68rem; color: var(--muted); line-height: 1.4;
    }}
  </style>
</head>
<body>
  <header id="preview-header">
    <div class="header-bar">
      <h1>异世界重生 · 正文预览</h1>
      <div class="header-actions">
        <span class="header-chip header-rev" id="preview-rev-chip" title="正文指纹">rev …</span>
        <button type="button" class="header-chip" id="preview-refresh-btn" title="强制拉取 GitHub 最新正文">更新</button>
        <button type="button" class="header-chip header-toggle" id="header-toggle" aria-expanded="false" aria-controls="header-panel">工具</button>
      </div>
    </div>
    <div class="header-panel" id="header-panel" hidden>
      <div class="meta" id="preview-meta">构建于 {built} · rev {revision_placeholder} · 跟踪 {html.escape(preview_branch)} · 源 {html.escape(' / '.join(sources))}</div>
      <div class="preview-toolbar">
        <span class="preview-sync-status" id="preview-sync-status">正在拉取最新正文…</span>
      </div>
      <p class="header-hint">打开/点「更新」会绕过 htmlpreview 缓存，直接从 GitHub 拉正文热替换。备用直链见工具说明。</p>
      <p class="header-hint" id="preview-alt-link">备用（无 htmlpreview）：<a href="https://cdn.jsdelivr.net/gh/{html.escape(repo)}@{html.escape(preview_branch)}{html.escape(raw_path)}" target="_blank" rel="noopener">jsDelivr 直开</a></p>
    </div>
  </header>
{toc}
  <main id="preview-main"><article id="preview-article">{body}</article></main>
  <footer id="preview-status" hidden></footer>
  <script>
    (function () {{
      var REFRESH_MS = {refresh_ms};
      var HIDDEN_REFRESH_MS = Math.max(REFRESH_MS, 5 * 60 * 1000);
      var SCROLL_KEY = "novel-preview-scroll";
      var REPO = {json.dumps(repo)};
      var BRANCH = {json.dumps(preview_branch)};
      var RAW_PATH = {json.dumps(raw_path)};
      var VIEWER_BASE = {json.dumps(viewer_base)};
      var CURRENT_SHA = {json.dumps(drafts_sha)};
      var CURRENT_REVISION = {json.dumps(revision_placeholder)};
      var checking = false;
      var pollTimer = null;

      function rawUrlForRef(ref, ts) {{
        var url = "https://raw.githubusercontent.com/" + REPO + "/" + ref + RAW_PATH;
        if (ts) url += (url.indexOf("?") >= 0 ? "&" : "?") + "t=" + ts;
        return url;
      }}

      function jsdelivrUrlForRef(ref, ts) {{
        var url = "https://cdn.jsdelivr.net/gh/" + REPO + "@" + ref + RAW_PATH;
        if (ts) url += (url.indexOf("?") >= 0 ? "&" : "?") + "t=" + ts;
        return url;
      }}

      function viewerUrlForRef(ref, ts) {{
        return VIEWER_BASE + rawUrlForRef(ref, ts);
      }}

      /* raw 顶栏误开 → 跳回 htmlpreview（稳定 preview 分支书签）
         注意：raw 常按 text/plain 下发，脚本未必执行；真正防跳走靠下方锚点拦截 */
      if (
        window.location.hostname === "raw.githubusercontent.com" &&
        window.top === window
      ) {{
        var keepHash = window.location.hash || "";
        window.location.replace(viewerUrlForRef(BRANCH, Date.now()) + keepHash);
        return;
      }}

      function setStatus(text, cls) {{
        var el = document.getElementById("preview-sync-status");
        if (!el) return;
        el.textContent = text;
        el.className = "preview-sync-status" + (cls ? " " + cls : "");
      }}

      function setRevChip(rev) {{
        var chip = document.getElementById("preview-rev-chip");
        if (!chip) return;
        var short = (rev || CURRENT_REVISION || "").slice(0, 8) || "…";
        chip.textContent = "rev " + short;
      }}

      function setButtonBusy(busy) {{
        var btn = document.getElementById("preview-refresh-btn");
        if (!btn) return;
        btn.disabled = !!busy;
        btn.textContent = busy ? "…" : "更新";
      }}

      setRevChip(CURRENT_REVISION);

      /* 页眉默认折叠，少占阅读空间 */
      (function initHeaderCollapse() {{
        var header = document.getElementById("preview-header");
        var toggle = document.getElementById("header-toggle");
        var panel = document.getElementById("header-panel");
        if (!header || !toggle || !panel) return;
        var KEY = "novel-preview-header-expanded";
        function apply(expanded) {{
          header.classList.toggle("is-expanded", expanded);
          panel.hidden = !expanded;
          toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
          toggle.textContent = expanded ? "收起" : "工具";
          try {{ localStorage.setItem(KEY, expanded ? "1" : "0"); }} catch (e) {{}}
        }}
        var saved = null;
        try {{ saved = localStorage.getItem(KEY); }} catch (e) {{}}
        apply(saved === "1");
        toggle.addEventListener("click", function () {{
          apply(!header.classList.contains("is-expanded"));
        }});
      }})();

      function saveScrollPosition() {{
        try {{
          sessionStorage.setItem(
            SCROLL_KEY,
            JSON.stringify({{
              y: window.scrollY || document.documentElement.scrollTop || 0
            }})
          );
        }} catch (e) {{}}
      }}

      function restoreScrollPosition() {{
        try {{
          var raw = sessionStorage.getItem(SCROLL_KEY);
          if (!raw) return;
          var saved = JSON.parse(raw);
          if (typeof saved.y !== "number") return;
          function apply() {{
            window.scrollTo(0, saved.y);
          }}
          apply();
          requestAnimationFrame(apply);
          window.setTimeout(apply, 120);
        }} catch (e) {{}}
      }}

      if (document.readyState === "loading") {{
        document.addEventListener("DOMContentLoaded", restoreScrollPosition);
      }} else {{
        restoreScrollPosition();
      }}

      var scrollTimer = null;
      window.addEventListener("scroll", function () {{
        if (scrollTimer) window.clearTimeout(scrollTimer);
        scrollTimer = window.setTimeout(saveScrollPosition, 200);
      }}, {{ passive: true }});

      function extractMeta(html, name) {{
        var re = new RegExp('meta name="' + name + '" content="([^"]+)"');
        var m = html.match(re);
        return m ? m[1] : null;
      }}

      function extractDraftsSha(html) {{
        return extractMeta(html, "drafts-sha");
      }}

      function extractPreviewRevision(html) {{
        return extractMeta(html, "preview-revision");
      }}

      function remoteFingerprint(html) {{
        return extractPreviewRevision(html) || extractDraftsSha(html) || "";
      }}

      function localArticleText() {{
        var el = document.getElementById("preview-article");
        return el ? (el.textContent || "").replace(/\\s+/g, " ").trim() : "";
      }}

      function remoteArticleText(html) {{
        var doc = parseRemoteDocument(html);
        if (!doc) return "";
        var el = doc.getElementById("preview-article") || doc.querySelector("main article");
        return el ? (el.textContent || "").replace(/\\s+/g, " ").trim() : "";
      }}

      function parseRemoteDocument(html) {{
        try {{
          return new DOMParser().parseFromString(html, "text/html");
        }} catch (e) {{
          return null;
        }}
      }}

      /* 页内热替换：不整页走 htmlpreview，直接换正文 */
      function applyHotSwap(html) {{
        var doc = parseRemoteDocument(html);
        if (!doc) return false;
        var remoteArticle = doc.getElementById("preview-article") || doc.querySelector("main article");
        var localArticle = document.getElementById("preview-article") || document.querySelector("main article");
        if (!remoteArticle || !localArticle) return false;

        saveScrollPosition();
        localArticle.innerHTML = remoteArticle.innerHTML;

        var remoteToc = doc.getElementById("toc-drawer");
        var localToc = document.getElementById("toc-drawer");
        if (remoteToc && localToc) localToc.innerHTML = remoteToc.innerHTML;

        var remoteMeta = doc.getElementById("preview-meta") || doc.querySelector("header .meta");
        var localMeta = document.getElementById("preview-meta");
        if (remoteMeta && localMeta) localMeta.textContent = remoteMeta.textContent;

        ["drafts-sha", "preview-revision", "build-script-sha", "build-commit", "built-at"].forEach(function (name) {{
          var val = extractMeta(html, name);
          var node = document.querySelector('meta[name="' + name + '"]');
          if (val && node) node.setAttribute("content", val);
        }});

        CURRENT_REVISION = extractPreviewRevision(html) || CURRENT_REVISION;
        CURRENT_SHA = extractDraftsSha(html) || CURRENT_SHA;
        setRevChip(CURRENT_REVISION);
        restoreScrollPosition();
        return true;
      }}

      function navigateToLatest(ref) {{
        saveScrollPosition();
        var target = viewerUrlForRef(ref || BRANCH, Date.now());
        try {{
          if (window.top !== window) {{
            window.top.location.replace(target);
            return;
          }}
        }} catch (e) {{}}
        window.location.replace(target);
      }}

      function fetchHtml(url) {{
        return fetch(url, {{
          cache: "no-store",
          credentials: "omit",
          headers: {{ "Cache-Control": "no-cache", Pragma: "no-cache" }},
        }}).then(function (res) {{
          if (!res.ok) throw new Error("fetch " + res.status);
          return res.text();
        }});
      }}

      /* 多源：文件最新 commit raw → 分支 tip raw → jsDelivr */
      function fetchLatestHtml(commitSha) {{
        var ts = Date.now();
        var tries = [];
        if (commitSha) tries.push(function () {{ return fetchHtml(rawUrlForRef(commitSha, ts)); }});
        tries.push(function () {{ return fetchHtml(rawUrlForRef(BRANCH, ts)); }});
        tries.push(function () {{ return fetchHtml(jsdelivrUrlForRef(commitSha || BRANCH, ts)); }});
        var i = 0;
        function next() {{
          if (i >= tries.length) return Promise.reject(new Error("all sources failed"));
          return tries[i++]().catch(next);
        }}
        return next();
      }}

      function fetchPreviewTipSha() {{
        /* 只问改过 standalone.html 的最新 commit，避免被无关 commit 误导 */
        var path = RAW_PATH.replace(/^\\//, "");
        var apiUrl =
          "https://api.github.com/repos/" +
          REPO +
          "/commits?path=" +
          encodeURIComponent(path) +
          "&sha=" +
          encodeURIComponent(BRANCH) +
          "&per_page=1";
        return fetch(apiUrl, {{
          cache: "no-store",
          credentials: "omit",
          headers: {{ Accept: "application/vnd.github+json" }},
        }})
          .then(function (res) {{
            if (!res.ok) throw new Error("api " + res.status);
            return res.json();
          }})
          .then(function (list) {{
            if (list && list[0] && list[0].sha) return list[0].sha;
            throw new Error("empty commits");
          }})
          .catch(function () {{
            return fetch(
              "https://api.github.com/repos/" + REPO + "/commits/" + encodeURIComponent(BRANCH),
              {{
                cache: "no-store",
                credentials: "omit",
                headers: {{ Accept: "application/vnd.github+json" }},
              }}
            ).then(function (res) {{
              if (!res.ok) throw new Error("api tip " + res.status);
              return res.json();
            }}).then(function (commit) {{
              return commit && commit.sha ? commit.sha : null;
            }});
          }});
      }}

      /**
       * force=true：手动/首屏 —— 拉到就热替换（正文文本不同或指纹不同）
       * force=false：轮询 —— 仅指纹变化才换
       */
      function syncFromRemote(force) {{
        if (checking) return;
        checking = true;
        if (force) setButtonBusy(true);
        setStatus(force ? "正在拉取最新正文…" : "后台检查中…");

        fetchPreviewTipSha()
          .catch(function () {{ return null; }})
          .then(function (sha) {{
            return fetchLatestHtml(sha).then(function (html) {{
              var remoteFp = remoteFingerprint(html);
              var remoteText = remoteArticleText(html);
              var localText = localArticleText();
              var fpChanged = remoteFp && remoteFp !== CURRENT_REVISION && remoteFp !== CURRENT_SHA;
              var textChanged = remoteText && remoteText !== localText;
              if (force) {{
                if (textChanged || fpChanged || remoteFp !== CURRENT_REVISION) {{
                  if (applyHotSwap(html)) {{
                    setStatus(
                      (textChanged ? "已热更新（绕过缓存）· " : "已对齐最新 · ") +
                        "rev " +
                        (CURRENT_REVISION || "").slice(0, 8),
                      "is-new"
                    );
                  }} else {{
                    setStatus("热更新失败，整页重载…", "is-err");
                    navigateToLatest(sha || BRANCH);
                  }}
                }} else {{
                  var now = new Date();
                  var hh = String(now.getHours()).padStart(2, "0");
                  var mm = String(now.getMinutes()).padStart(2, "0");
                  setStatus("已是最新 · " + hh + ":" + mm + " · rev " + (CURRENT_REVISION || "").slice(0, 8));
                  setRevChip(CURRENT_REVISION);
                }}
              }} else if (fpChanged || textChanged) {{
                if (applyHotSwap(html)) {{
                  setStatus("已热更新 · rev " + (CURRENT_REVISION || "").slice(0, 8), "is-new");
                }}
              }} else {{
                setStatus("已是最新 · rev " + (CURRENT_REVISION || "").slice(0, 8));
              }}
            }});
          }})
          .catch(function () {{
            setStatus("拉取失败：可点「更新」，或打开工具里的 jsDelivr 备用链", "is-err");
          }})
          .then(function () {{
            checking = false;
            setButtonBusy(false);
          }});
      }}

      function schedulePoll() {{
        if (pollTimer) window.clearInterval(pollTimer);
        var ms = document.visibilityState === "hidden" ? HIDDEN_REFRESH_MS : REFRESH_MS;
        pollTimer = window.setInterval(function () {{
          syncFromRemote(false);
        }}, ms);
      }}

      var btn = document.getElementById("preview-refresh-btn");
      if (btn) {{
        btn.addEventListener("click", function () {{
          syncFromRemote(true);
        }});
      }}

      /* 首屏强制拉一次：即使 htmlpreview 吐旧壳，也会换成 GitHub 最新正文 */
      syncFromRemote(true);
      schedulePoll();
      document.addEventListener("visibilitychange", function () {{
        schedulePoll();
        if (document.visibilityState === "visible") syncFromRemote(true);
      }});
      window.addEventListener("focus", function () {{
        syncFromRemote(false);
      }});
      window.addEventListener("pageshow", function () {{
        syncFromRemote(true);
      }});
    }})();
  </script>
  <script>
    (function () {{
      var toggle = document.getElementById("toc-toggle");
      var closeBtn = document.getElementById("toc-close");
      var drawer = document.getElementById("toc-drawer");
      var backdrop = document.getElementById("toc-backdrop");
      if (!toggle || !drawer || !backdrop) return;

      function openToc() {{
        drawer.hidden = false;
        backdrop.hidden = false;
        requestAnimationFrame(function () {{ drawer.classList.add("is-open"); }});
        toggle.setAttribute("aria-expanded", "true");
        document.body.style.overflow = "hidden";
      }}

      function closeToc() {{
        drawer.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
        window.setTimeout(function () {{
          if (!drawer.classList.contains("is-open")) {{
            drawer.hidden = true;
            backdrop.hidden = true;
          }}
        }}, 220);
      }}

      /* htmlpreview 会把 #锚点 解析成 raw.githubusercontent.com/...#锚点，
         一点目录就丢掉阅读前缀、变成源码页。拦截后只做页内滚动。 */
      function findHashTarget(hash) {{
        if (!hash || hash.charAt(0) !== "#") return null;
        var raw = hash.slice(1);
        var candidates = [raw];
        try {{
          var decoded = decodeURIComponent(raw);
          if (decoded !== raw) candidates.push(decoded);
        }} catch (e) {{}}
        for (var i = 0; i < candidates.length; i++) {{
          var el = document.getElementById(candidates[i]);
          if (el) return {{ el: el, hash: "#" + candidates[i] }};
        }}
        return null;
      }}

      function stayOnViewerHash(hash) {{
        try {{
          if (window.location.hostname === "htmlpreview.github.io") {{
            var base = window.location.href.split("#")[0];
            history.replaceState(null, "", base + hash);
          }} else if (window.location.hostname !== "raw.githubusercontent.com") {{
            history.replaceState(null, "", hash);
          }}
        }} catch (e) {{}}
      }}

      function goToHash(hash) {{
        var hit = findHashTarget(hash);
        if (!hit) return false;
        hit.el.scrollIntoView({{ behavior: "smooth", block: "start" }});
        stayOnViewerHash(hit.hash);
        return true;
      }}

      document.addEventListener("click", function (e) {{
        var a = e.target && e.target.closest ? e.target.closest('a[href^="#"]') : null;
        if (!a) return;
        var href = a.getAttribute("href");
        if (!href || href === "#") return;
        if (!goToHash(href)) return;
        e.preventDefault();
        e.stopPropagation();
        if (toggle.getAttribute("aria-expanded") === "true") closeToc();
      }}, true);

      if (window.location.hash) {{
        window.setTimeout(function () {{ goToHash(window.location.hash); }}, 0);
      }}

      toggle.addEventListener("click", openToc);
      if (closeBtn) closeBtn.addEventListener("click", closeToc);
      backdrop.addEventListener("click", closeToc);
      document.addEventListener("keydown", function (e) {{
        if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") closeToc();
      }});
    }})();
  </script>
</body>
</html>
"""
    revision = preview_revision(page.replace(revision_placeholder, ""))
    page = page.replace(revision_placeholder, revision)
    OUT.write_text(page, encoding="utf-8")
    print(
        f"Wrote {OUT} ({built}) · revision {revision} · {len(chapters)} 章 · "
        + ", ".join(sources)
    )


if __name__ == "__main__":
    main()
