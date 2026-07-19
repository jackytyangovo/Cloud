# 正文预览（Preview）

> 手机 / 浏览器阅读正文，无需打开 IDE 文件树。

### 为何旧书签总是旧版？

直接收藏 `standalone.html` 时，**htmlpreview / raw / jsDelivr 都会缓存整页壳**。  
推送再新，书签仍可能打开几小时前的 HTML。

**办法**：书签改收藏 **启动页 `live.html`**——壳几乎不变；**每次打开**都问 GitHub「standalone 最新 commit」，再按 **commit SHA** 拉正文写进页面。这样书签本身不用改，也能跟上推送。

### 人读 vs 机器读

| 用途 | 链接 |
|------|------|
| **人读（请换这个书签）** | 下方 **方案 A · live 启动页** |
| **Agent / 对源码** | `raw.githubusercontent.com/.../standalone.html` |

### 正文同步规则（✓ 用户确认）

| 情况 | 预览收录 |
|------|----------|
| 该章已有 `finalized/*.md` | **用定稿** |
| 尚无定稿、仅有 `drafts/*.md` | **用初稿** |

重建：`python3 novel-project/preview/build_standalone.py`（改 `drafts/` / `finalized/` 后 rebuild 或等 Actions）。

---

## 方案 A · 即时书签（推荐 · live 启动页）

### 稳定方案（推荐）：仓库自带 GitHub Pages

**不必另建网站。** 第三方预览缓存太凶，手机上经常假旧。  
请按 [`ENABLE-GITHUB-PAGES.md`](./ENABLE-GITHUB-PAGES.md) **点一次设置**，然后只收藏：

https://jackytyangovo.github.io/Cloud/

### 不启用 Pages 时：先在 GitHub 上核对初稿

https://github.com/jackytyangovo/Cloud/blob/cursor/style-check-prologue-129b/novel-project/drafts/chapter-001.md#L55

这里能直接看到「堂弟芬恩 / 堂哥埃里克」（证明已推送，问题只在预览壳）。

| 机制 | 说明 |
|------|------|
| 启动页 | `live.html` 每次打开 → API 查 tip SHA → 拉该 SHA 的 `standalone.html` |
| Actions 发布 | push 正文 / 定时 → rebuild → 推到 `preview`，并尽量 purge jsDelivr |
| 页内「更新」 | 进入正文后仍可热替换 |
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
| 继续收藏旧的 **`standalone.html` 书签** | CDN/htmlpreview 粘旧壳；请改收藏 **live.html** |
| 收藏 / 分享 **不带** `htmlpreview` 的 raw 链 | 当纯文本源码显示 |
| 只靠「下拉刷新」htmlpreview | 对旧壳无效；换 live 书签后每次打开会重拉 tip |

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `preview-config.json` | 仓库名、`preview` 书签分支、`source_branch`、轮询间隔 |
| `live.html` | **人读书签启动页**（每次按 tip SHA 拉最新 standalone） |
| `index.html` | 本地实时预览（fetch 草稿；与 preview 分支根 index 不同） |
| `standalone.html` | 正文整页（由脚本生成；勿再当书签） |
| `build_standalone.py` | 从定稿/初稿重建 + 内嵌热更新脚本 |
| `server.py` | 本地 HTTP（8765） |
| `.github/workflows/preview-refresh.yml` | 定时/push 重建并发布到 `preview` |

---

## 排障清单

1. 书签是否已换成 **方案 A**（`.../Cloud/preview/...`）？  
2. 点 **「立即检查更新」**，状态是否变为「已热更新」？  
3. 仍旧 → 试 **方案 C** jsDelivr，或 purge 后再开  
4. 仍旧 → 用 **方案 D** 钉当前 commit，确认文件本身是否已 push  
5. 桌面调试用 **方案 E**
