# 异世界重生 · 小说项目

长篇连载异世界小说设定库与大纲。采用**滚动大纲**模式：多卷开放，不预设结局，世界观随剧情补充。

## 项目结构

```
novel-project/
├── bible/           # 设定圣经
│   ├── style-guide.md
│   ├── outline.md   # 大纲（当前：卷一「觉醒」）
│   ├── characters.md
│   ├── worldbuilding.md
│   └── timeline.md
├── chapters/        # 正文（待开写）
└── setup_project.py
```

## 快速导航

| 文档 | 内容 |
|------|------|
| [**WORKFLOW.md**](novel-project/WORKFLOW.md) | **模型分工**：Composer 2.5 修 bible / Sonnet 5 写正文 |
| [outline.md](novel-project/bible/outline.md) | **完整大纲** · 卷一关键章节拍 + 伏笔 |
| [worldbuilding.md](novel-project/bible/worldbuilding.md) | 魔法/剑术、种族、地理、势力 |
| [characters.md](novel-project/bible/characters.md) | 莉莉娅、莱恩菲尔家、人物关系 |
| [timeline.md](novel-project/bible/timeline.md) | 前史与卷一时间轴 |
| [style-guide.md](novel-project/bible/style-guide.md) | 视角、文风、战力约束 |

## 核心设定摘要

- **主角**：莉莉娅·莱恩菲尔（Lilia Lenfiel），6 岁女，前世 25 岁男性记忆，男转女
- **天赋**：光系·净章（表）+ 生命（隐，中期）
- **开局**：灰谷王国小贵族；觉醒前一月记忆觉醒
- **模式**：土著觉醒前世记忆，非肉体穿越

## 初始化

```bash
python novel-project/setup_project.py
```
