#!/usr/bin/env python3
"""生成 novel-project/preview/standalone.html（GitHub Pages 人读预览）。

需求见 REQUIREMENTS.md：
- 定稿优先，否则初稿
- 书签：https://jackytyangovo.github.io/Cloud/
- Pages 上仅同源更新，目录页内跳转
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
    "preview_branch": "preview",
    "source_branch": "cursor/style-check-prologue-129b",
    "refresh_interval_minutes": 2,
}

CHAPTER_NAME_RE = re.compile(r"^(prologue|chapter-\d+)\.md$", re.IGNORECASE)


def load_config() -> dict:
    if CONFIG_PATH.is_file():
        return {**DEFAULT_CONFIG, **json.loads(CONFIG_PATH.read_text(encoding="utf-8"))}
    return dict(DEFAULT_CONFIG)


def chapter_anchor(label: str) -> str:
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
        items.append((f"{path.parent.name}/{path.name}", label_from_md(path)))
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


def content_hash(chapters: list[tuple[str, str]]) -> str:
    h = hashlib.sha256()
    for rel, _ in chapters:
        path = ROOT / rel
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()[:12]


def script_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]


def git_short_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT.parent,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def preview_revision(page: str) -> str:
    return hashlib.sha256(page.encode("utf-8")).hexdigest()[:16]


def build_toc(chapters: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f'      <li><a href="#{html.escape(chapter_anchor(label), quote=True)}">{html.escape(label)}</a></li>'
        for _, label in chapters
    )
    return f"""  <button type="button" class="toc-toggle" id="toc-toggle" aria-expanded="false" aria-controls="toc-drawer">目录</button>
  <div class="toc-backdrop" id="toc-backdrop" hidden></div>
  <nav class="toc-drawer" id="toc-drawer" aria-label="目录" hidden>
    <div class="toc-header">
      <span class="toc-title">目录</span>
      <button type="button" class="toc-close" id="toc-close" aria-label="关闭">×</button>
    </div>
    <ol class="toc-list">
{items}
    </ol>
  </nav>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build standalone.html for GitHub Pages")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config = load_config()
    refresh_min = max(1, int(config.get("refresh_interval_minutes", 2)))
    refresh_ms = refresh_min * 60 * 1000
    chapters = discover_chapters()
    if not chapters:
        raise SystemExit("No chapters found in finalized/ or drafts/")

    c_hash = content_hash(chapters)
    s_hash = script_hash()

    if OUT.is_file() and not args.force:
        existing = OUT.read_text(encoding="utf-8")
        if (
            f'content="{c_hash}"' in existing
            and f'content="{s_hash}"' in existing
            and 'meta name="preview-revision"' in existing
        ):
            print(f"Preview up to date (content {c_hash}, script {s_hash})")
            return

    sources = []
    sections = []
    for rel, label in chapters:
        path = ROOT / rel
        md_html = md_to_html(path.read_text(encoding="utf-8"))
        anchor = chapter_anchor(label)
        sections.append((label, anchor, md_html))
        kind = "定稿" if rel.startswith("finalized/") else "初稿"
        sources.append(f"{label.split(' · ', 1)[0]}←{kind}")

    body = "\n".join(
        f'<section id="{html.escape(anchor)}" class="chapter-section">'
        f'<h2 class="chapter">{html.escape(label)}</h2>{content}</section>'
        for label, anchor, content in sections
    )
    toc = build_toc(chapters)
    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sha = git_short_sha()
    title_bits = [label.split(" · ", 1)[0] for _, label in chapters[:3]]
    title_suffix = " · ".join(title_bits)
    if len(chapters) > 3:
        title_suffix += "…"
    source_line = " / ".join(sources)
    rev_ph = "__PREVIEW_REVISION__"

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <meta name="drafts-sha" content="{c_hash}" />
  <meta name="preview-revision" content="{rev_ph}" />
  <meta name="build-script-sha" content="{s_hash}" />
  <meta name="build-commit" content="{html.escape(sha)}" />
  <meta name="built-at" content="{html.escape(built)}" />
  <title>小说正文预览 · {html.escape(title_suffix)}</title>
  <style>
    :root {{
      --bg: #faf8f5; --text: #2c2825; --muted: #7a7268;
      --card: #fff; --border: #e8e2d9; --scene: #c4b8a8; --accent: #8b6914;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #1c1a18; --text: #ebe6df; --muted: #a39a8e;
        --card: #262320; --border: #3a342e; --scene: #6a5f52; --accent: #d4a84b;
      }}
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0; background: var(--bg); color: var(--text);
      font: 17px/1.85 "PingFang SC", "Noto Sans SC", "Source Han Sans SC", sans-serif;
      -webkit-text-size-adjust: 100%;
    }}
    header {{
      position: sticky; top: 0; z-index: 20;
      background: color-mix(in srgb, var(--card) 92%, transparent);
      backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--border);
    }}
    .header-bar {{
      display: flex; align-items: center; justify-content: space-between;
      gap: 8px; padding: 8px 12px; min-height: 44px;
    }}
    header h1 {{
      margin: 0; font-size: .95rem; font-weight: 600;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .header-actions {{ display: flex; align-items: center; gap: 6px; flex-shrink: 0; }}
    .header-chip {{
      border: 1px solid var(--border); background: var(--bg);
      color: var(--text); border-radius: 999px;
      padding: 3px 10px; font: inherit; font-size: .72rem;
      cursor: pointer; line-height: 1.3;
    }}
    .header-chip:hover, .header-chip:focus {{ border-color: var(--accent); outline: none; }}
    .header-chip:disabled {{ opacity: .55; cursor: wait; }}
    .header-panel {{
      display: none; padding: 0 12px 10px; border-top: 1px solid var(--border);
    }}
    header.is-expanded .header-panel {{ display: block; }}
    .meta {{ font-size: .72rem; color: var(--muted); margin: 8px 0 0; line-height: 1.45; }}
    .sync {{ font-size: .72rem; color: var(--muted); margin-top: 6px; }}
    .sync.is-new {{ color: var(--accent); font-weight: 600; }}
    .sync.is-err {{ color: #b42318; }}
    main {{ max-width: 38rem; margin: 0 auto; padding: 1.25rem 1rem 4rem; }}
    section.chapter-section {{ margin-bottom: 2.5em; scroll-margin-top: 3.2rem; }}
    h2.chapter {{ font-size: 1.25rem; text-align: center; margin: 0 0 1em; }}
    article h2 {{ font-size: 1.05rem; margin: 1.4em 0 .7em; font-weight: 600; }}
    article p {{ margin: 0 0 .9em; text-indent: 2em; }}
    article p.no-indent {{ text-indent: 0; text-align: center; color: var(--muted); }}
    hr.scene {{
      border: 0; border-top: 1px solid var(--scene);
      margin: 1.6em auto; width: 30%;
    }}
    aside.setting-note {{
      margin: 1.2em 0; padding: .8em 1em;
      border-left: 3px solid var(--accent);
      background: color-mix(in srgb, var(--card) 80%, var(--bg));
      font-size: .92em; color: var(--muted);
    }}
    aside.setting-note p {{ text-indent: 0; margin: 0 0 .4em; }}
    .setting-label {{ font-weight: 600; color: var(--text); }}
    .toc-toggle {{
      position: fixed; right: 12px; bottom: 16px; z-index: 30;
      border: 1px solid var(--border); background: var(--card);
      color: var(--text); border-radius: 999px;
      padding: 10px 16px; font: inherit; font-size: .85rem;
      box-shadow: 0 4px 16px rgba(0,0,0,.08); cursor: pointer;
    }}
    .toc-backdrop {{
      position: fixed; inset: 0; background: rgba(0,0,0,.28); z-index: 40;
    }}
    .toc-drawer {{
      position: fixed; top: 0; right: 0; bottom: 0; width: min(84vw, 20rem);
      background: var(--card); z-index: 50; border-left: 1px solid var(--border);
      transform: translateX(100%); transition: transform .2s ease;
      display: flex; flex-direction: column;
    }}
    .toc-drawer.is-open {{ transform: translateX(0); }}
    .toc-header {{
      display: flex; align-items: center; justify-content: space-between;
      padding: 12px 14px; border-bottom: 1px solid var(--border);
    }}
    .toc-title {{ font-weight: 600; }}
    .toc-close {{
      border: 0; background: transparent; color: var(--muted);
      font-size: 1.4rem; line-height: 1; cursor: pointer; padding: 4px 8px;
    }}
    .toc-list {{ margin: 0; padding: 12px 8px 24px 2rem; overflow: auto; }}
    .toc-list a {{
      display: block; padding: .45em 0; color: var(--text); text-decoration: none;
    }}
    .toc-list a:hover, .toc-list a:focus {{ color: var(--accent); }}
  </style>
</head>
<body>
  <header id="preview-header">
    <div class="header-bar">
      <h1>异世界重生 · 正文预览</h1>
      <div class="header-actions">
        <button type="button" class="header-chip" id="preview-refresh-btn">更新</button>
        <button type="button" class="header-chip" id="header-toggle" aria-expanded="false">工具</button>
      </div>
    </div>
    <div class="header-panel" id="header-panel" hidden>
      <div class="meta" id="preview-meta">构建 {html.escape(built)} · rev {rev_ph} · {html.escape(source_line)}</div>
      <div class="sync" id="preview-sync-status">就绪</div>
    </div>
  </header>
{toc}
  <main id="preview-main"><article id="preview-article">{body}</article></main>
  <script>
    (function () {{
      var REFRESH_MS = {refresh_ms};
      var CURRENT_REVISION = {json.dumps(rev_ph)};
      var checking = false;

      function $(id) {{ return document.getElementById(id); }}

      function setStatus(text, cls) {{
        var el = $("preview-sync-status");
        if (!el) return;
        el.textContent = text;
        el.className = "sync" + (cls ? " " + cls : "");
      }}

      function meta(name) {{
        var node = document.querySelector('meta[name="' + name + '"]');
        return node ? node.getAttribute("content") : null;
      }}

      function extractMeta(html, name) {{
        var m = html.match(new RegExp('meta name="' + name + '" content="([^"]+)"'));
        return m ? m[1] : null;
      }}

      /* —— 页眉折叠 —— */
      (function () {{
        var header = $("preview-header");
        var toggle = $("header-toggle");
        var panel = $("header-panel");
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

      /* —— 目录：页内滚动，不改写地址到外站 —— */
      (function () {{
        var toggle = $("toc-toggle");
        var closeBtn = $("toc-close");
        var drawer = $("toc-drawer");
        var backdrop = $("toc-backdrop");
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
          setTimeout(function () {{
            if (!drawer.classList.contains("is-open")) {{
              drawer.hidden = true;
              backdrop.hidden = true;
            }}
          }}, 220);
        }}
        function goHash(hash) {{
          if (!hash || hash.charAt(0) !== "#") return false;
          var id = hash.slice(1);
          try {{ id = decodeURIComponent(id); }} catch (e) {{}}
          var el = document.getElementById(id);
          if (!el) return false;
          el.scrollIntoView({{ behavior: "smooth", block: "start" }});
          try {{ history.replaceState(null, "", "#" + id); }} catch (e) {{}}
          return true;
        }}
        document.addEventListener("click", function (e) {{
          var a = e.target && e.target.closest ? e.target.closest('a[href^="#"]') : null;
          if (!a) return;
          var href = a.getAttribute("href");
          if (!href || href === "#") return;
          if (!goHash(href)) return;
          e.preventDefault();
          e.stopPropagation();
          if (toggle.getAttribute("aria-expanded") === "true") closeToc();
        }}, true);
        toggle.addEventListener("click", openToc);
        if (closeBtn) closeBtn.addEventListener("click", closeToc);
        backdrop.addEventListener("click", closeToc);
        document.addEventListener("keydown", function (e) {{
          if (e.key === "Escape") closeToc();
        }});
        if (location.hash) setTimeout(function () {{ goHash(location.hash); }}, 0);
      }})();

      /* —— 同源热更新（仅 github.io；不加自定义请求头） —— */
      function onPages() {{
        return /\\.github\\.io$/i.test(location.hostname || "");
      }}
      function pagesBase() {{
        var path = location.pathname || "/";
        if (/\\.html?$/i.test(path)) path = path.replace(/\\/[^\\/]*$/, "/");
        else if (path.slice(-1) !== "/") path += "/";
        return location.origin + path;
      }}
      function articleText() {{
        var el = $("preview-article");
        return el ? (el.textContent || "").replace(/\\s+/g, " ").trim() : "";
      }}
      function applyHotSwap(html) {{
        var doc;
        try {{ doc = new DOMParser().parseFromString(html, "text/html"); }}
        catch (e) {{ return false; }}
        var remote = doc.getElementById("preview-article");
        var local = $("preview-article");
        if (!remote || !local) return false;
        local.innerHTML = remote.innerHTML;
        var remoteToc = doc.getElementById("toc-drawer");
        var localToc = $("toc-drawer");
        if (remoteToc && localToc) localToc.innerHTML = remoteToc.innerHTML;
        var remoteMeta = doc.getElementById("preview-meta");
        var localMeta = $("preview-meta");
        if (remoteMeta && localMeta) localMeta.textContent = remoteMeta.textContent;
        ["drafts-sha", "preview-revision", "build-script-sha", "build-commit", "built-at"].forEach(function (name) {{
          var val = extractMeta(html, name);
          var node = document.querySelector('meta[name="' + name + '"]');
          if (val && node) node.setAttribute("content", val);
        }});
        CURRENT_REVISION = extractMeta(html, "preview-revision") || CURRENT_REVISION;
        return true;
      }}
      function sync(force) {{
        if (!onPages()) {{
          if (force) setStatus("当前非 Pages，请打开 github.io 书签阅读", "is-err");
          return;
        }}
        if (checking) return;
        checking = true;
        var btn = $("preview-refresh-btn");
        if (btn && force) {{ btn.disabled = true; btn.textContent = "…"; }}
        if (force) setStatus("检查更新…");
        var ts = Date.now();
        var base = pagesBase();
        var urls = [base + "standalone.html?t=" + ts, base + "index.html?t=" + (ts + 1)];
        var i = 0;
        function next() {{
          if (i >= urls.length) return Promise.reject(new Error("fail"));
          return fetch(urls[i++], {{ cache: "no-store", credentials: "omit", mode: "cors" }})
            .then(function (res) {{
              if (!res.ok) throw new Error(String(res.status));
              return res.text();
            }})
            .catch(next);
        }}
        next()
          .then(function (html) {{
            var remoteRev = extractMeta(html, "preview-revision");
            var doc = new DOMParser().parseFromString(html, "text/html");
            var remoteArt = doc.getElementById("preview-article");
            var remoteText = remoteArt
              ? (remoteArt.textContent || "").replace(/\\s+/g, " ").trim()
              : "";
            var localText = articleText();
            var changed = (remoteRev && remoteRev !== CURRENT_REVISION) || (remoteText && remoteText !== localText);
            if (changed) {{
              if (applyHotSwap(html)) setStatus("已更新 · rev " + (CURRENT_REVISION || "").slice(0, 8), "is-new");
              else setStatus("更新失败，请下拉刷新整页", "is-err");
            }} else {{
              var now = new Date();
              setStatus(
                "已是最新 · " +
                  String(now.getHours()).padStart(2, "0") +
                  ":" +
                  String(now.getMinutes()).padStart(2, "0")
              );
            }}
          }})
          .catch(function () {{
            if (force) setStatus("检查失败，请稍后重试或刷新整页", "is-err");
          }})
          .then(function () {{
            checking = false;
            if (btn) {{ btn.disabled = false; btn.textContent = "更新"; }}
          }});
      }}

      var refreshBtn = $("preview-refresh-btn");
      if (refreshBtn) refreshBtn.addEventListener("click", function () {{ sync(true); }});
      if (onPages()) {{
        setTimeout(function () {{ sync(false); }}, 400);
        setInterval(function () {{
          if (document.visibilityState === "visible") sync(false);
        }}, REFRESH_MS);
        document.addEventListener("visibilitychange", function () {{
          if (document.visibilityState === "visible") sync(false);
        }});
      }} else {{
        setStatus("请用 GitHub Pages 书签阅读");
      }}
    }})();
  </script>
</body>
</html>
"""

    revision = preview_revision(page.replace(rev_ph, ""))
    page = page.replace(rev_ph, revision)
    OUT.write_text(page, encoding="utf-8")
    print(
        f"Wrote {OUT} ({built}) · revision {revision} · {len(chapters)} 章 · "
        + ", ".join(sources)
    )


if __name__ == "__main__":
    main()
