# 正文预览（Preview）

> 手机 / 浏览器阅读正文，无需打开 IDE 文件树。

## 方式一 · 手机推荐（自动刷新）

改稿并 **push 后**，打开下面链接；页面 **每 30 秒自动刷新**，拉取最新 `standalone.html`。

**预览地址（push 后可用）：**

https://htmlpreview.github.io/?https://raw.githubusercontent.com/jackytyangovo/Cloud/cursor/isekai-novel-outline-1688/novel-project/preview/standalone.html

也可在 GitHub 仓库中直接打开：`novel-project/preview/standalone.html` → **Raw** 或 **View file**（视浏览器而定）。

### 更新流程（Agent / 本地）

正文改动 `drafts/*.md` 后，运行：

```bash
python3 novel-project/preview/build_standalone.py
git add novel-project/preview/standalone.html novel-project/drafts/
git commit && git push
```

推送后，手机预览页在 **30 秒内** 刷新即可看到新稿。

---

## 方式二 · 本地实时预览（3 秒刷新）

适合桌面 Cursor，改 `drafts/` **保存即更新**，无需 push。

```bash
python3 novel-project/preview/server.py
```

浏览器打开：**http://127.0.0.1:8765/preview/**

- 每 **3 秒** 自动拉取 `drafts/prologue.md`
- 后续章节可在 `index.html` 的下拉框中扩展

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `index.html` | 本地实时预览（fetch 草稿） |
| `standalone.html` | 手机离线页（内嵌正文，由脚本生成） |
| `build_standalone.py` | 从 `drafts/` 重建 standalone |
| `server.py` | 本地 HTTP 服务（8765 端口） |
