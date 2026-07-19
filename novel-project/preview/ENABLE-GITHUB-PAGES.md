# 一键稳定预览：启用 GitHub Pages（不必另建网站）

第三方（htmlpreview / jsDelivr / raw.githack）会缓存旧页，手机上经常看到旧正文。  
**不必自己买域名、搭服务器**——用本仓库自带的 GitHub Pages 即可。

## 你只需做一次（约 1 分钟）

1. 打开：https://github.com/jackytyangovo/Cloud/settings/pages  
2. **Build and deployment → Source** 选其一：  
   - **推荐**：`GitHub Actions`（已有工作流 `Deploy preview to GitHub Pages`）  
   - 或：`Deploy from a branch` → Branch 选 **`preview`** → Folder **`/`** → Save  
3. 等 1～2 分钟出现站点地址。

## 之后请只收藏

https://jackytyangovo.github.io/Cloud/

推送预览后，这个地址会更新。顶栏应显示 **`堂✓`**（表示正文含堂哥/堂弟）；若是 **`堂✗`** 说明仍是旧壳。

## 不启用 Pages 时，如何确认「其实已经改好了」

直接看 GitHub 网页上的初稿（不经任何预览 CDN）：

https://github.com/jackytyangovo/Cloud/blob/cursor/style-check-prologue-129b/novel-project/drafts/chapter-001.md#L55

应看到：

- `搂住凑过来的堂弟芬恩`
- `最后下来的是堂哥埃里克`
