#!/usr/bin/env python3
"""从 drafts/*.md 生成可离线/手机浏览的 standalone.html"""
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
OUT = PREVIEW / "standalone.html"
CONFIG_PATH = PREVIEW / "preview-config.json"
DEFAULT_CONFIG = {
    "github_repo": "jackytyangovo/Cloud",
    "preview_branch": "cursor/isekai-novel-outline-1688",
    "refresh_interval_minutes": 5,
    "htmlpreview_base": "https://htmlpreview.github.io/?",
}

CHAPTERS = [
    ("drafts/prologue.md", "序章 · 错位的清晨"),
    ("drafts/chapter-001.md", "第一章 · 两家莱恩菲尔"),
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
    h = hashlib.sha256()
    for rel, _ in chapters:
        path = ROOT / rel.replace("drafts/", "drafts/")
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
    parser = argparse.ArgumentParser(description="Build standalone.html from drafts/")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild even when drafts content hash is unchanged",
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
                f"Preview up to date (drafts {drafts_sha}, script {script_sha}), "
                "skip rebuild. Use --force to refresh."
            )
            return

    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sha = git_short_sha()
    branch = git_branch()
    repo = config["github_repo"]
    preview_branch = config.get("preview_branch") or branch
    raw_url = (
        f"https://raw.githubusercontent.com/{repo}/{preview_branch}"
        f"/novel-project/preview/standalone.html"
    )
    viewer_base = config.get("htmlpreview_base", DEFAULT_CONFIG["htmlpreview_base"])
    viewer_url = f"{viewer_base}{raw_url}"
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
      padding: 14px 16px; box-shadow: 0 1px 8px rgba(0,0,0,.06);
    }}
    header h1 {{ margin: 0 0 6px; font-size: 1.1rem; }}
    .meta {{ font-size: .78rem; color: var(--muted); }}
    .toc-toggle {{
      position: fixed; top: 4.6rem; right: 14px; z-index: 30;
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
      padding: 16px; max-width: 42rem; margin: 0 auto;
    }}
    @media (max-width: 720px) {{
      .toc-toggle {{ top: auto; bottom: 18px; right: 16px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>异世界重生 · 正文预览</h1>
    <div class="meta">构建于 {built} · commit {sha} · 分支 {html.escape(branch)} · 打开/切回即检查 · 每 {refresh_min} 分钟轮询</div>
  </header>
{toc}
  <main><article>{body}</article></main>
  <footer id="preview-status">手机阅读：打开/切回页面即检查更新 · 每 {refresh_min} 分钟轮询 · 滚动位置会保留</footer>
  <script>
    (function () {{
      var REFRESH_MS = {refresh_ms};
      var SCROLL_KEY = "novel-preview-scroll";
      var RAW_URL = {json.dumps(raw_url)};
      var VIEWER_BASE = {json.dumps(viewer_base)};
      var CURRENT_SHA = {json.dumps(drafts_sha)};
      var CURRENT_REVISION = {json.dumps(revision_placeholder)};

      function bustRawUrl(ts) {{
        return RAW_URL + (RAW_URL.indexOf("?") >= 0 ? "&" : "?") + "t=" + ts;
      }}

      function viewerUrl(ts) {{
        return VIEWER_BASE + bustRawUrl(ts);
      }}

      /* raw.githubusercontent.com 顶栏打开时浏览器只显示源码；若脚本仍能执行则跳回预览器 */
      if (
        window.location.hostname === "raw.githubusercontent.com" &&
        window.top === window
      ) {{
        window.location.replace(viewerUrl(Date.now()));
        return;
      }}

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

      function extractDraftsSha(html) {{
        var m = html.match(/meta name="drafts-sha" content="([^"]+)"/);
        return m ? m[1] : null;
      }}

      function extractPreviewRevision(html) {{
        var m = html.match(/meta name="preview-revision" content="([^"]+)"/);
        return m ? m[1] : null;
      }}

      function isRemoteNewer(html) {{
        var remoteRev = extractPreviewRevision(html);
        if (remoteRev && remoteRev !== CURRENT_REVISION) return true;
        if (!remoteRev) {{
          var remoteSha = extractDraftsSha(html);
          return remoteSha && remoteSha !== CURRENT_SHA;
        }}
        return false;
      }}

      function navigateToLatest() {{
        saveScrollPosition();
        var target = viewerUrl(Date.now());
        try {{
          if (window.top !== window) {{
            window.top.location.replace(target);
            return;
          }}
        }} catch (e) {{}}
        window.location.replace(target);
      }}

      function checkForUpdate() {{
        var checkUrl = bustRawUrl(Date.now());
        fetch(checkUrl, {{ cache: "no-store", credentials: "omit" }})
          .then(function (res) {{
            if (!res.ok) return null;
            return res.text();
          }})
          .then(function (text) {{
            if (!text) return;
            if (isRemoteNewer(text)) navigateToLatest();
          }})
          .catch(function () {{
            /* 网络/CDN 抖动时不刷新、不报错，避免白屏 */
          }});
      }}

      checkForUpdate();
      window.setInterval(checkForUpdate, REFRESH_MS);
      document.addEventListener("visibilitychange", function () {{
        if (document.visibilityState === "visible") checkForUpdate();
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

      toggle.addEventListener("click", openToc);
      if (closeBtn) closeBtn.addEventListener("click", closeToc);
      backdrop.addEventListener("click", closeToc);
      drawer.querySelectorAll("a").forEach(function (link) {{
        link.addEventListener("click", closeToc);
      }});
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
    print(f"Wrote {OUT} ({built}) · revision {revision} · {len(chapters)} 章")


if __name__ == "__main__":
    main()
