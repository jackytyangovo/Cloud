# 小说项目工作流（Workflow）

> 防止模型分工搞混：**Composer 2.5 修缮 bible**，**Sonnet 5 撰写正文**。

---

## 模型分工（固定）

| 任务 | 模型 | Cursor 模式 | 可改动的目录 |
|------|------|-------------|--------------|
| 大纲、设定、人物、时间线 | **Composer 2.5** | Plan → Agent | `novel-project/bible/` |
| 正文撰写、文风润色 | **Sonnet 5** | Agent | `novel-project/drafts/` |
| 预览 / 审阅正文 | 任意 | Ask / Agent | **只读** `novel-project/drafts/` |
| 快速查设定、讨论剧情 | 任意 | Ask | 只读，不改文件 |

**单一事实来源**：所有设定以 `bible/` 为准。正文不得擅自新增或改写世界观；发现设定缺口应停下，回到 Composer 补 bible。

### 世界观自动入库（Composer 必做）

用户确认或补充**城市、势力、制度、地理**等设定时，Composer **不要只在对话里回复**，须自动：

1. 写入 `worldbuilding.md`（完整条目）
2. 更新 `outline.md` → **「世界观速查」**（摘要 + 关联章节）
3. 若影响人物/行程 → 同步 `characters.md`、`timeline.md`、相关章节拍

### 命名原则（硬规则 · 西方中世纪奇幻）

凡**官职、爵位、机构、议会席位、城市职官、司署/官厅**等专名，Composer 在**起中文名时**须始终贴合**西方中世纪奇幻**背景，**禁止**现代官僚或东方官制语感。

| 做 | 不做 |
|----|------|
| 先定 **Western  medieval/fantasy 原文**，再译中文 | 先造「某某司 / 某某署 / 某某局 / 某某长」式中文，再硬贴英文 |
| 中文用 **执政、监护、执公、城卫、关税官、河域** 等封建/自治市语感 | **司长、部长、处、局、科、厅** 等近现代或东方六部制用语 |
| bible 每条专名并列 **中文称号 + Western 原文** | 仅中文、无 Western 对照 |
| 参考：英制封建、自治市特许状、Sheriff/Bailiff/Reeve/Warden、Parliament Estates | 参考：明清官制、现代政府部委、日式「XX省 XX局」 |

**示例（灰港已定）**：

- ✓ **河域副监** · Underwarden（小贵族任副官；非「河运司长」）
- ✓ **河域长官** · River Warden（官厅主官；高于副监）
- ✓ **城邦执政** · Burgomaster（非泛用「市长」作制度专名时）
- ✓ **执公** · Bailiff（非「执达吏」）
- ✓ **城卫队长** · Captain of the Watch（非「城防司长」）

正文（Sonnet）引用官职时以 bible 定稿为准；若发现命名漂移，回 Composer 统一 bible。

### 章节大纲边界（硬规则）

| 规则 | 说明 |
|------|------|
| **用户未提不写** | 用户未提及的情节线、势力出场、制度冲突等，**不擅自加入** `outline.md` 章节拍 |
| **6 岁近期禁止** | 莉莉娅现 **6 岁**：近期章节**不得**出现联姻/订婚/婚约政治、王室或政治高层直接接触 |
| **中期再开** | 王室、艾什伯恩、帝国中枢、联姻政治等 → **小说中期**再细规划；bible 世界观可保留背景，**不排进近期章节** |

---

## 对话怎么开

### 对话 A：大纲修缮（Composer 2.5）

- **用途**：补设定、改章节拍、更新人物表、调整时间线
- **建议标题**：`大纲修缮` 或 `bible维护`
- **不要**在此对话里写正文

**典型开场**：

```
请根据我的补充更新 bible：
- [你的设定条目]

只修改 novel-project/bible/ 下相关文件，不要动 drafts/。
```

**建议 @ 文件**：

- `novel-project/bible/outline.md`
- `novel-project/bible/worldbuilding.md`
- `novel-project/bible/characters.md`
- `novel-project/bible/style-guide.md`
- `novel-project/bible/timeline.md`

---

### 对话 B：正文写作（Sonnet 5）

- **用途**：按大纲写章、改文风、润色对话与心理描写
- **建议标题**：`正文 Ch.XXX`（一章一对话，或按卷开对话）
- **不要**在此对话里改 `bible/`（除非我明确说「同步回 bible」）

**典型开场**：

```
请根据 @novel-project/bible/outline.md 的 Ch.N 撰写正文，
写入 @novel-project/drafts/chapter-00N.md。

严格遵守 @novel-project/bible/style-guide.md：
- 第一人称「我」（莉莉娅）为主；必要时短段第三人称旁白补设定
- 平直简单语言
- 兼顾动作、神态、语言、环境变化、主角心理
- 设定以 bible 为准，不擅自新增世界观
- 天赋净阶 ≠ 即战力

约 3000 字。不要修改 bible/ 文件。
```

**建议 @ 文件**：

- 当前章对应 `outline.md` 节拍
- `style-guide.md`
- 必要时 `characters.md`、`worldbuilding.md`（只读参考）
- 上一章正文（保持衔接）

---

## 迭代循环

```
Composer 2.5 更新 bible
        ↓
Sonnet 5 写 / 改 drafts/
        ↓
你审阅
        ↓
├─ 设定问题 → 回对话 A（Composer）
└─ 文风 / 节奏 / 对话 → 对话 B（Sonnet）
```

| 你想改的内容 | 找谁 |
|--------------|------|
| 爵位、天赋、家族、章节拍、伏笔 | **Composer 2.5** |
| 句子太平/太文、心理太少、环境没写 | **Sonnet 5** |
| 大纲结构要大改 | Composer 改 bible → Sonnet 重写受影响章节 |

---

## 目录边界（硬规则）

```
novel-project/
├── bible/          ← Composer 2.5 专属
│   ├── outline.md
│   ├── worldbuilding.md
│   ├── characters.md
│   ├── style-guide.md
│   └── timeline.md
├── drafts/         ← 正文（Sonnet 5 撰写；预览某章读此目录）
│   └── chapter-NNN.md
└── chapters/       ← 遗留目录（如有旧稿；以 drafts/ 为准）
```

- **Composer** 默认可写：`bible/`、`README.md`（索引）、`WORKFLOW.md`
- **Sonnet** 默认可写：`drafts/`
- **预览正文**：用户说「预览 Ch.N」→ 读 `drafts/chapter-NNN.md`（不存在则告知未撰写）
- 跨目录修改需你**明确指示**

---

## Sonnet 5 写作检查清单（每章）

- [ ] 与 `outline.md` 当前章节拍一致
- [ ] 文风符合 `style-guide.md`（平直、四层兼顾）
- [ ] 战力未膨胀（孩童高净阶不碾压成人）
- [ ] 未擅自定稿标有 `【随剧情补充】` 的设定
- [ ] 章末有悬念或情绪落点

---

## Composer 2.5 修缮检查清单

- [ ] 改动已写入对应 bible 文件
- [ ] `outline` / `characters` / `timeline` 三处信息一致
- [ ] **新专名符合「西方中世纪奇幻」命名原则**（见上文「命名原则」）
- [ ] **近期章节未擅自加入**联姻/订婚、王室及政治高层（除非用户已要求）
- [ ] 未误改正文
- [ ] 滚动大纲：卷二及以后仍标 `【随剧情补充】` 处不强行定稿

---

## 开写顺序建议

1. 用 **Composer** 确认卷一 Ch.1–2 大纲无误
2. 新建 **Sonnet** 对话，写 `drafts/chapter-001.md`
3. 你审阅 → 文风问题留 Sonnet，设定问题回 Composer
4. Ch.1 满意后，Sonnet 继续 Ch.2（@ 上一章正文）

---

## 常见误操作

| 误操作 | 后果 | 正确做法 |
|--------|------|----------|
| 在 Sonnet 对话里改 outline | bible 与正文两套版本 | 回 Composer 改 bible，再让 Sonnet 对齐 |
| 在 Composer 对话里写正文 | 文风/节奏不如 Sonnet | 新开 Sonnet 对话写 drafts/ |
| 预览正文去 chapters/ 找 | 目录已迁 | **优先** `drafts/chapter-NNN.md` |
| 同一对话混用两个模型 | 上下文混乱 | 大纲对话、正文对话分开 |
| 正文时未 @ style-guide | 文风漂移 | 每次写章都 @ style-guide |
