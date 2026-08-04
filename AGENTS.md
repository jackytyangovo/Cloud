# AGENTS.md

## Cursor Cloud specific instructions

### What this repo is
This repository is a Git-managed **Chinese isekai novel authoring workspace** plus a small
Python **preview pipeline**. It is *not* a web service/SaaS: there is no database, no Node,
no Docker, and no third-party packages — the tooling is **Python 3 standard library only**.

The `main` branch is essentially a placeholder (`README.md`). The actual novel content and
the preview tooling live on feature branches (for example `cursor/isekai-novel-outline-1688`).
When working on novel content, branch from the relevant content branch rather than `main`,
otherwise `novel-project/` will not be present.

### Layout (on a content branch)
- `novel-project/bible/` — worldbuilding, outline, characters, style guides
- `novel-project/drafts/` — work-in-progress chapters (Markdown)
- `novel-project/finalized/` — locked chapter snapshots
- `novel-project/preview/` — the preview pipeline (see below)
- `.cursor/rules/` and `.cursor/skills/isekai-novel-writing/SKILL.md` — writing workflow rules

### Environment / dependencies
No install step is required. `python3` (3.12+) is already available and is the only runtime
needed. The update script is intentionally a near no-op.

### Running the preview (services)
There is only one product with two run modes, both defined under `novel-project/preview/`
(see `novel-project/preview/README.md`, in Chinese, for full details):

- **Live local preview server** — `python3 novel-project/preview/server.py`
  Serves `novel-project/` at `http://127.0.0.1:8765/preview/` (binds `0.0.0.0:8765`).
  The `index.html` page fetches `drafts/*.md` directly, so editing a draft and reloading
  the page shows the change (no rebuild needed).
- **Static standalone build** — `python3 novel-project/preview/build_standalone.py`
  Regenerates `novel-project/preview/standalone.html` (self-contained mobile/offline reader).

### Non-obvious gotchas
- `build_standalone.py` **skips the rebuild** when the drafts content hash is unchanged; pass
  `--force` to rebuild anyway (e.g. to refresh the header timestamp).
- The chapter set embedded in `standalone.html` is the **hardcoded `CHAPTERS` list** near the
  top of `build_standalone.py`, not an automatic scan of `drafts/`. Add new chapters there.
- `server.py` runs forever in the foreground; start it in a background terminal/tmux session.
- `preview-config.json` pins the GitHub repo/branch used by the deployed htmlpreview flow; the
  local server does not need it.
