# 正文预览（Preview）

> 手机 / 浏览器阅读正文，无需打开 IDE 文件树。

## 方式一 · 手机 / GitHub 预览（改稿即重建并 push）

**不再使用页面定时刷新。** 每次改动 `drafts/*.md` 后，Agent / 本地须 **立即** 重建 `standalone.html` 并 **push**，读者 **手动刷新** 预览页即可看到新稿。

**预览地址（push 后可用）：**

- **推荐（按 commit 固定，避免 CDN 缓存旧稿）：**  
  `https://htmlpreview.github.io/?https://raw.githubusercontent.com/jackytyangovo/Cloud/<commit>/novel-project/preview/standalone.html`  
  将 `<commit>` 换为页眉显示的短 SHA（如 `028f0bf`）。

- **分支最新（可能需等 1–2 分钟或强制刷新）：**  
  https://htmlpreview.github.io/?https://raw.githubusercontent.com/jackytyangovo/Cloud/cursor/isekai-novel-outline-1688/novel-project/preview/standalone.html

也可在 GitHub 仓库中直接打开：`novel-project/preview/standalone.html` → **View file**（看页眉 **构建于 … UTC · commit …** 是否最新）。

### 更新流程（硬规则 · 每次改稿必做）

```bash
python3 novel-project/preview/build_standalone.py
git add novel-project/preview/standalone.html novel-project/drafts/
git commit && git push -u origin <branch>
```

- **一次改稿 = 一次 rebuild + 一次 push**（**必须**与 `drafts/` 同批提交 `standalone.html`，禁止只 push md 不 rebuild）
- 页眉 **构建于 … UTC · commit …** 可核对；看不到新稿时用 **带 commit 的链接** 或浏览器 **强制刷新**

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
| `index.html` | 本地实时预览（fetch 草稿） |
| `standalone.html` | 手机离线页（内嵌正文，由脚本生成） |
| `build_standalone.py` | 从 `drafts/` 重建 standalone |
| `server.py` | 本地 HTTP 服务（8765 端口） |
