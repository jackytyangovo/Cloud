# 正文预览（Preview）

> 手机 / 浏览器阅读正文，无需打开 IDE 文件树。

## 方式一 · 手机 / GitHub 预览（自动刷新 + 定时 push）

**两层同步（默认每 5 分钟）：**

1. **GitHub Actions**（`.github/workflows/preview-refresh.yml`）  
   - 每 **5 分钟**检查 `drafts/` 是否有未编入 `standalone.html` 的改动  
   - 有改动则 **rebuild + push**（无改动不提交，避免空 commit）  
   - `drafts/` push 时也会 **立即**触发同一流程  

2. **预览页**（`standalone.html` 内嵌脚本）  
   - 打开后每 **5 分钟**自动 **带缓存破除参数刷新** 当前页，减轻 raw/CDN 旧稿  

**预览分支** 见 `preview-config.json` 的 `preview_branch`（当前：`cursor/isekai-novel-outline-1688`）。

**预览地址（推荐分支最新）：**

https://htmlpreview.github.io/?https://raw.githubusercontent.com/jackytyangovo/Cloud/cursor/isekai-novel-outline-1688/novel-project/preview/standalone.html

也可按 commit 固定（页眉短 SHA）：

`https://htmlpreview.github.io/?https://raw.githubusercontent.com/jackytyangovo/Cloud/<commit>/novel-project/preview/standalone.html`

页眉 **构建于 … UTC · commit … · 每 5 分钟自动刷新** 可核对是否最新。

### 改稿时（Agent / 本地）

```bash
python3 novel-project/preview/build_standalone.py
git add novel-project/drafts/ novel-project/preview/standalone.html
git commit && git push -u origin <branch>
```

- **仍建议改稿同批 rebuild + push**（读者不必等最多 5 分钟）  
- 若只 push 了 `drafts/*.md` 忘了 rebuild，**5 分钟内** Actions 会补推 `standalone.html`  
- 强制重建（drafts 未变也更新页眉时间）：`python3 novel-project/preview/build_standalone.py --force`  
- 自动刷新会 **记住滚动位置**（`sessionStorage`），刷新后回到原阅读处

---

## 方式二 · 本地实时预览

适合桌面 Cursor，改 `drafts/` **保存即更新**（fetch 草稿 md，非 standalone）。

```bash
python3 novel-project/preview/server.py
```

浏览器打开：**http://127.0.0.1:8765/preview/**

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `preview-config.json` | 预览分支、刷新间隔、GitHub 仓库名 |
| `index.html` | 本地实时预览（fetch 草稿） |
| `standalone.html` | 手机离线页（内嵌正文，由脚本生成） |
| `build_standalone.py` | 从 `drafts/` 重建 standalone |
| `server.py` | 本地 HTTP 服务（8765 端口） |
