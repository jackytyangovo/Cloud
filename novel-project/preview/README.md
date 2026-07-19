# 正文预览（Preview）

> 手机 / 浏览器阅读正文，无需打开 IDE 文件树。  
> **更新不及时**时，优先用下方 **方案 A** 书签 + 页内「立即检查更新」。

### 人读 vs 机器读（务必分清）

| 用途 | 链接形态 |
|------|----------|
| **人读（阅读模式）** | 必须带前缀 `https://htmlpreview.github.io/?` + raw 地址 |
| **Agent / 对源码** | 直接用 `https://raw.githubusercontent.com/.../standalone.html`（纯 HTML 文本） |

没有 `htmlpreview` 前缀时，浏览器会把页面当源码显示，不适合阅读。  
目录跳转已在页内拦截：点「第一章」只会滚动到对应章节，**不会**丢掉前缀跳到 raw。

### 正文同步规则（✓ 用户确认）

| 情况 | 预览收录 |
|------|----------|
| 该章已有 `finalized/*.md` | **用定稿** |
| 尚无定稿、仅有 `drafts/*.md` | **用初稿** |

重建命令不变：`python3 novel-project/preview/build_standalone.py`（改 `drafts/` 或 `finalized/` 后都要 rebuild / 等 Actions）。

### 推流与刷新（2026-07-19 起）

| 层 | 做法 |
|----|------|
| **发布源** | Actions 定时/手动从 **`source_branch`（当前写作分支）** 重建，再推到 `preview`；不再从旧 outline 盖书签 |
| **打开页面** | 首屏 **强制** 向 GitHub 拉最新 `standalone.html`，正文热替换（绕过 htmlpreview 旧壳） |
| **点「更新」** | 同上强制拉取；顶栏 `rev xxxxxxxx` 为正文指纹，变了才算刷到新版 |
| **备用直链** | 不用 htmlpreview： [jsDelivr 直开](https://cdn.jsdelivr.net/gh/jackytyangovo/Cloud@preview/novel-project/preview/standalone.html)（若旧：先开 [purge](https://purge.jsdelivr.net/gh/jackytyangovo/Cloud@preview/novel-project/preview/standalone.html)） |

若仍看到「侧翼 / 盖伦一系」等旧句：先看顶栏 **rev** 是否变化 → 点「更新」→ 或改用 jsDelivr 备用。

---

## 方案 A · 稳定书签（推荐）

固定跟踪仓库的 **`preview` 分支**（Actions 会把各分支刚生成的 `standalone.html` 同步过来）。

**书签（一次收藏，长期有效）：**

https://htmlpreview.github.io/?https://raw.githubusercontent.com/jackytyangovo/Cloud/preview/novel-project/preview/standalone.html

| 机制 | 说明 |
|------|------|
| Actions 发布 | push `drafts/` 或 `finalized/` / 定时每 **2 分钟** → rebuild → 推到 `preview` 分支 |
| 页内热更新 | 发现新 `preview-revision` 时 **替换正文**，不整页白屏、少受 htmlpreview 二次缓存影响 |
| 立即检查 | 页头按钮 **「立即检查更新」**；切回 App / 聚焦窗口也会检查 |
| 轮询 | 前台约 **1 分钟**；后台约 **5 分钟** |
| 多源拉取 | GitHub API → **commit 固定 raw** → **jsDelivr** → branch raw |

页眉默认折叠为一条细栏（标题 +「更新」+「工具」）；点「工具」展开构建信息与同步状态。「已是最新 / 已热更新」写在展开面板里。

---

## 方案 B · 工作分支直链（开发中看本分支）

看 **尚未合并** 的 feature 分支时用（把分支名换成当前分支）：

```
https://htmlpreview.github.io/?https://raw.githubusercontent.com/jackytyangovo/Cloud/<branch>/novel-project/preview/standalone.html
```

例：`cursor/style-check-prologue-129b`  
日常阅读仍建议 **方案 A**，避免每个分支换书签。

---

## 方案 C · jsDelivr 备用（绕过 raw CDN）

GitHub `raw` 分支 CDN 常缓存约 5 分钟，且 `?t=` **破不了**。可用 jsDelivr：

```
https://cdn.jsdelivr.net/gh/jackytyangovo/Cloud@preview/novel-project/preview/standalone.html
```

- 浏览器直接打开即可（不必套 htmlpreview）  
- 若仍旧：打开  
  `https://purge.jsdelivr.net/gh/jackytyangovo/Cloud@preview/novel-project/preview/standalone.html`  
  清缓存后再刷  
- 页内脚本在 API/raw 失败时也会自动试 jsDelivr

---

## 方案 D · commit 钉死链接（核对某一版）

页眉或 `git rev-parse --short HEAD` 取短 SHA：

```
https://htmlpreview.github.io/?https://raw.githubusercontent.com/jackytyangovo/Cloud/<commit>/novel-project/preview/standalone.html
```

适合确认「刚 push 的那一版」是否已进预览；不适合当日常书签。

---

## 方案 E · 本地实时预览（桌面）

改 `drafts/` **保存即更新**（fetch md，不经 GitHub）：

```bash
python3 novel-project/preview/server.py
```

浏览器：**http://127.0.0.1:8765/preview/**

---

## 改稿时（Agent / 本地）

```bash
python3 novel-project/preview/build_standalone.py
git add novel-project/drafts/ novel-project/preview/standalone.html
git commit && git push -u origin <branch>
```

- **仍建议改稿同批 rebuild + push**（不必干等 Actions）  
- 忘了 rebuild：最多约 **2 分钟** Actions 会补建，并发布到 **`preview` 分支**  
- 强制重建：`python3 novel-project/preview/build_standalone.py --force`

---

## 勿做

| 勿 | 原因 |
|----|------|
| 收藏 / 分享 **不带** `htmlpreview.github.io/?` 的 raw 链 | 当纯文本源码显示；人读必须用方案 A/B |
| 只靠「下拉刷新」htmlpreview | 中间层/CDN 可能仍吐旧页；用页内按钮或方案 C |
| 以为 feature 分支 push 会改旧书签 | 旧书签若仍指向 `outline-1688`，请改收藏 **方案 A** |

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `preview-config.json` | 仓库名、`preview` 书签分支、`source_branch`、轮询间隔 |
| `index.html` | 本地实时预览（fetch 草稿） |
| `standalone.html` | 手机页（内嵌正文，由脚本生成） |
| `build_standalone.py` | 从 `drafts/` 重建 + 内嵌热更新脚本 |
| `server.py` | 本地 HTTP（8765） |
| `.github/workflows/preview-refresh.yml` | 定时/push 重建并发布到 `preview` |

---

## 排障清单

1. 书签是否已换成 **方案 A**（`.../Cloud/preview/...`）？  
2. 点 **「立即检查更新」**，状态是否变为「已热更新」？  
3. 仍旧 → 试 **方案 C** jsDelivr，或 purge 后再开  
4. 仍旧 → 用 **方案 D** 钉当前 commit，确认文件本身是否已 push  
5. 桌面调试用 **方案 E**
