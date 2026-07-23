# 预览页需求（用户确认汇总 · 2026-07-19）

## 书签与打开方式

1. **唯一人读书签**：GitHub Pages  
   `https://jackytyangovo.github.io/Cloud/`  
2. **禁止**再把 htmlpreview / jsDelivr / raw.githack / raw 当主书签（会粘旧壳或显示源码）。  
3. Agent 对源码可用：`raw.githubusercontent.com/.../standalone.html`。

## 正文收录

1. **有定稿** → 用 `finalized/`  
2. **无定稿、仅有初稿** → 用 `drafts/`  
3. 当前：序章←空（插叙待构思）；第一–三章←定稿；第四章←初稿（仅标题）。

## 阅读体验

1. 手机可读：字号、行距、段首缩进适合竖屏。  
2. **目录**：页内打开；点章节只滚动，不跳出站点。  
3. 页眉可折叠；**不要**「堂✓」一类调试芯片。  
4. 「更新」按钮：检查本站是否有新版并热替换正文。

## 更新机制（硬约束）

1. 在 `github.io` 上 **只从同源** 拉 `standalone.html` / `index.html`。  
2. **禁止**用 jsDelivr / raw 旧壳覆盖 Pages 正文。  
3. `fetch` **不加** `Cache-Control` 等自定义头（会 CORS 失败）。  
4. 推送后由 Actions 重建并发布到 `preview` 分支根目录（`index.html` = 全文）。

## 发布

1. 写作分支改稿 → `build_standalone.py` → push。  
2. Actions 同步到 `preview`：`index.html` + `standalone.html`。  
3. Pages 跟踪 `preview` 分支根目录（需仓库主人启用一次）。
