# 正文预览

需求全文见 [`REQUIREMENTS.md`](./REQUIREMENTS.md)。

## 人读书签（唯一）

https://jackytyangovo.github.io/Cloud/

须已启用 GitHub Pages（一次设置，见 [`ENABLE-GITHUB-PAGES.md`](./ENABLE-GITHUB-PAGES.md)）。

| 规则 | 说明 |
|------|------|
| 正文源 | **定稿优先**；无定稿用初稿 |
| 更新 | Pages 上只拉**同源**新版，不经第三方 CDN |
| 目录 | 页内滚动，不跳出站点 |
| Agent 看源码 | `raw.githubusercontent.com/.../standalone.html` |

## 改稿后重建

```bash
python3 novel-project/preview/build_standalone.py --force
git add novel-project/drafts/ novel-project/finalized/ novel-project/preview/standalone.html
git commit && git push
```

Actions 会发布到 `preview` 分支根目录（`index.html` = 全文）。

## 文件

| 文件 | 用途 |
|------|------|
| `REQUIREMENTS.md` | 预览需求汇总 |
| `ENABLE-GITHUB-PAGES.md` | 启用 Pages 步骤 |
| `build_standalone.py` | 生成 `standalone.html` |
| `standalone.html` | 生成物（勿手改） |
| `preview-config.json` | 仓库 / 分支 / 轮询间隔 |
| `index.html` / `server.py` | 本地实时预览（桌面改稿用） |
