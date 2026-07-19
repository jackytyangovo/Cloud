# 小说项目工作流（Workflow）

> 防止分工搞混：**设定修缮** 以 `bible/` 为准；**正文撰写** 写 `drafts/`，**不限定模型**（任意 Agent 均可）。

---

## 模型分工（固定）

| 任务 | 执行者 | Cursor 模式 | 可改动的目录 |
|------|--------|-------------|--------------|
| 大纲、设定、人物、时间线 | **设定修缮**（常为 Composer 2.5） | Plan → Agent | `novel-project/bible/` |
| 正文撰写、文风润色 | **任意 Agent**（**不指定 Sonnet**） | Agent | `novel-project/drafts/` |
| 正文预览 / 审阅 | 任意 | Ask / Agent | **只读** `novel-project/drafts/` · 手机见 `preview/standalone.html` |
| 快速查设定、讨论剧情 | 任意 | Ask | 只读，不改文件 |

**单一事实来源**：所有设定以 `bible/` 为准。正文不得擅自新增或改写世界观；发现设定缺口应停下，补 `bible/`（或请用户明确后同步）。

### 当前优先（用户确认 · 2026-07-17 更新）

1. **正文撰写与润色**（`drafts/`）——**序章、第一章已定稿**（`finalized/prologue.md` · `finalized/chapter-001.md`）；后续章工作稿迭代中
2. **样文文风分析**（用户发样章 → 更新 `style-reference.md` / `style-guide.md`）
3. **大纲与设定补充**（`bible/`）——随正文审阅 **同步回 bible**（用户明确要求时）
4. 用户已确认章节拍 **保留在 `outline.md`**，不删
5. **补充入口**：见 `outline.md` → **「大纲补充 · 待填清单」**

### 样文入库流程（用户确认）

用户发来**样文/样章**时，负责 bible 的 Agent **须**：

1. **分析**：视角、句长、语气、结构、对话占比、心理/环境/R18 笔法等（不照搬原文情节）
2. **写入** `bible/style-reference.md`：追加或更新对应章节；在「样章索引」登记日期与类型
3. **同步** `style-guide.md`：仅当样文涉及硬规则（视角、R18 边界、卷一前期基调等）时微调
4. **不改** `drafts/`；**不**因样文擅自改世界观（除非用户明确要求）

**典型开场**：

```
请分析以下样文文风，写入 bible/style-reference.md：
[粘贴样文]
只改 style-reference.md / style-guide.md，不动 drafts/ 和 outline 情节。
```

---

用户确认或补充**城市、势力、制度、地理**等设定时，负责 bible 的 Agent **不要只在对话里回复**，须自动：

1. 写入 `worldbuilding.md`（完整条目）
2. 更新 `outline.md` → **「世界观速查」**（摘要 + 关联章节）
3. 若影响行程 → 同步 `timeline.md`、相关章节拍；**人物设定**见下条（勿因世界补丁擅自改 `characters.md`）

用户**明确要求**写入/改人物设定，或**明确定名并吩咐入库**时，负责 bible 的 Agent 才可：

1. 写入/改 `characters.md`（条目 + **按章区形象** + 出场记录表 + 必要时关系图）
2. 回填 `outline.md` 相关章节拍 / 首次出场表
3. 若涉职官/机构 → 同步 `worldbuilding.md`（Western 对照）

> **`characters.md` 只读默认**：写作、纠察、正文补细节时 **只查不改**。无用户点名 **禁止** 从正文回填形象、擅自增补容貌/性格行。  
> **人设按章区**：采用 **恒定设定 + 按章区形象表**；写第 N 章只取对应章区行，勿用后续章区状态写当前章。

### 命名原则（硬规则 · 西方中世纪奇幻）

凡**官职、爵位、机构、议会席位、城市职官、司署/官厅**等专名，在**起中文名时**须始终贴合**西方中世纪奇幻**背景，**禁止**现代官僚或东方官制语感。

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

正文引用官职时以 bible 定稿为准；若发现命名漂移，回 bible 统一。

### 章节大纲边界（硬规则）

| 规则 | 说明 |
|------|------|
| **用户未提不写** | 用户未提及的情节线、势力出场、制度冲突等，**不擅自加入** `outline.md` 章节拍 |
| **6 岁 · 联姻/订婚** | **可提及**社会背景（大人闲谈、制度一笔，如「十二岁才订」「净章将来好说亲」）；**不展开**订婚过程、媒妁、文书或「我」的婚约情节线 |
| **王室/高层** | 莉莉娅 **6–7 岁**卷内**不得**与王室或政治高层**直接接触**；联姻**政治线** → **中期**（12 岁+ 情节）再规划 |
| **卷界** | **卷一** = 6 岁→7 岁成长生活（**不含**入学许可、北上）；**Writ** 与学院 → **卷二**（**7 岁**） |
| **场景与情节** | **用户定场景/情节**；负责 bible 的 Agent **不擅自**分场景、不替用户想具体场次；仅在你要求时提供 **灵感备选**（可删改） |

---

## 对话怎么开

### 对话 A：大纲修缮（设定 · bible）

- **用途**：补设定、改章节拍、更新人物表、调整时间线
- **建议标题**：`大纲修缮` 或 `bible维护`
- **不要**在此对话里写正文（除非用户明确要求）

**典型开场**：

```
请根据我的补充更新 bible：
- [你的设定条目]

只修改 novel-project/bible/ 下相关文件，不要动 drafts/。
```

**建议 @ 文件**：

- `novel-project/bible/outline.md`
- `novel-project/bible/narrative-structure.md`
- `novel-project/bible/daily-growth-writing.md`
- `novel-project/bible/worldbuilding.md`
- `novel-project/bible/characters.md`
- `novel-project/bible/style-guide.md`
- `novel-project/bible/writing-essentials.md`（**纠察/写稿速查**）
- `novel-project/bible/timeline.md`

---

### 对话 B：正文写作（任意 Agent · drafts）

- **用途**：按大纲写章、改文风、润色对话与心理描写
- **模型**：**不限定**（Composer、Sonnet、Cloud Agent 等均可）
- **建议标题**：`正文 序章` / `正文 第X章`（一章一对话，或按卷开对话）
- **不要**在此对话里改 `bible/`（除非用户明确说「同步回 bible」）

**典型开场**：

```
请根据 @novel-project/bible/outline.md 的 **序章 / 第N章** 撰写正文，
写入 @novel-project/drafts/prologue.md（序章）或 @novel-project/drafts/chapter-NNN.md（第N章）。

严格遵守 @novel-project/bible/style-guide.md：
- 第一人称「我」（莉莉娅）为主；必要时短段第三人称旁白补设定
- 平直简单语言
- **初稿即正文**：outline/bible 只作情节边界参考，**严禁照办纲要**（不照译场次表、技法行、缩略语）
- 兼顾动作、神态、语言、环境变化、主角心理
- 设定以 bible 为准，不擅自新增世界观
- 天赋净阶 ≠ 即战力

约 3000 字。不要修改 bible/ 文件。
```

**建议 @ 文件**：

- [`WORKFLOW.md`](WORKFLOW.md)（流程与目录边界）
- 当前章对应 `outline.md` 节拍（**只读情节边界，严禁照译**）
- `writing-essentials.md`（**优先**）、`style-guide.md`、`style-reference.md`
- [`.cursor/skills/isekai-novel-writing/SKILL.md`](../.cursor/skills/isekai-novel-writing/SKILL.md)（写前/交稿自检）
- 必要时 `characters.md`、`worldbuilding.md`（只读参考）
- 上一章正文（保持衔接）

**改稿后必做**（预览）：

```bash
python3 novel-project/preview/build_standalone.py
git add novel-project/drafts/ novel-project/preview/standalone.html
git commit && git push
```

- **一次改稿 = rebuild + push** `standalone.html`（与正文同批；漏了 rebuild 时 **Actions 约 2 分钟**补推，并发布到稳定分支 `preview`）
- 手机书签请用 **`preview` 分支**（一书签长期有效）；页内有 **「立即检查更新」** 与热替换。详见 `preview/README.md`

**「全文」范围**（✓ 用户确认）：用户说 **「全文」** 默认指 **当前章节**（当次任务正在写的 `drafts/chapter-NNN.md` 或指定那一章）。**未点名其他章节时，不得改其他章初稿**；序章/定稿同步须用户 **明确点名**。

**用户序章定稿 pass**（✓ 用户确认）：用户以个人手法 **逐条** 修改序章；Agent **只改用户点名的部分**，每次记入 [`bible/user-style-iteration-log.md`](bible/user-style-iteration-log.md)（改前/改后/提炼）。pass 结束后 **汇总分析**，提取规则 **高优先级** 写入 `style-guide.md` / `style-reference.md` / 写作 skill，供后续章节模仿。

---

## 迭代循环

```
更新 bible/（设定修缮）
        ↓
任意 Agent 写 / 改 drafts/
        ↓
你审阅
        ↓
├─ 设定问题 → 回对话 A（bible）
└─ 文风 / 节奏 / 对话 → 对话 B（正文，同或换 Agent 均可）
```

| 你想改的内容 | 建议 |
|--------------|------|
| 爵位、天赋、家族、章节拍、伏笔 | **bible/** 修缮对话 |
| 句子、节奏、对话、润色 | **drafts/** 正文对话（任意 Agent） |
| 大纲结构要大改 | 先改 bible → 再改受影响章节正文 |

---

## 目录边界（硬规则）

```
novel-project/
├── bible/          ← 设定修缮（outline、worldbuilding…）
│   ├── outline.md
│   ├── narrative-structure.md   ← 日常·冒险·危机、1–3–9 埋线
│   ├── daily-growth-writing.md ← 日常成长期 4要4不要、章自查
│   ├── worldbuilding.md
│   ├── characters.md
│   ├── style-guide.md
│   ├── style-reference.md
│   ├── writing-essentials.md  ← 纠察/写稿速查
│   └── timeline.md
├── drafts/         ← 正文撰写与改稿（任意 Agent）
│   └── chapter-NNN.md
├── finalized/      ← 定稿快照（只读；仅用户说「章节定稿」时可写入）
│   └── prologue.md …
└── chapters/       ← 遗留目录（旧稿；以 drafts/ 为准）
```

- **bible/**：设定修缮默认可写；正文 Agent **只读**（除非用户**明确要求**同步回 bible）
- **`characters.md` 等参考设定**：**无用户点名不得改**（即使正文写了新形象细节，也**勿擅自回填**；等用户吩咐）
- **drafts/**：正文 Agent 可写；**不限定模型**
- **`finalized/`**：**禁止**日常修改；**仅**用户说 **「章节定稿」** 时复制 `drafts/` 快照入库
- **预览正文**：读 `drafts/`；**不读** `finalized/`

---

## 正文写作检查清单（每章）

写前读：`WORKFLOW.md` · **`writing-essentials.md` §〇模仿卡 + 红灯表（主对照）** · `style-guide.md` · `style-reference.md` · 写作 skill 自检表。

### 用户手改入库（硬 · 便于 Agent 模仿）

用户对正文做手改（推送 / 粘贴 / 逐句点名）后，负责正文或纠察的 Agent **须同轮**：

1. 写入 [`bible/writing-essentials.md`](bible/writing-essentials.md) **§〇 用户手改 · 模仿卡**（固定格式：`✗` 改前 / `✓` 改后 / `→` 以后怎么写）  
2. 追加 [`bible/user-style-iteration-log.md`](bible/user-style-iteration-log.md) 一条（改前/改后/提炼；有原话则记「为什么」）  
3. 若成硬规则 → 同步红灯表与 `style-guide.md`  
4. **禁止**只改正文却不入库；**禁止**无用户点名改 `characters.md`

### 读者看不懂的词（硬 · ✓）

用户以 **读者视角** 问某个词/说法看不懂 → **视为反例**（读者也看不懂）→ 正文避免；同轮写入要领 **红灯 #20**、「看不懂词表」、模仿卡，并改掉已出现处。

- [ ] **WORKFLOW 目录边界**：只改 `drafts/`；`finalized/` 仅用户说「章节定稿」；预览读 `drafts/`
- [ ] **「全文」= 当前章**；未点名不改其他章
- [ ] **初稿即正文**：**严禁照办纲要**（不照译场次表、技法行、bible 缩略语）
- [ ] 与 `outline.md` **情节边界**一致（非照抄纲要句式）
- [ ] 文风：先过 **`writing-essentials.md` 红灯表**；细则符合 `style-guide.md`
- [ ] 交稿前 **陌生读者视角** 通读一遍
- [ ] 战力未膨胀（孩童高净阶不碾压成人）
- [ ] 未擅自定稿标有 `【随剧情补充】` 的设定
- [ ] 章末有悬念或情绪落点
- [ ] 已 **rebuild + push** `preview/standalone.html`（改稿同批）

---

## 设定修缮检查清单（bible）

- [ ] 改动已写入对应 bible 文件
- [ ] `outline` / `characters` / `timeline` 三处信息一致
- [ ] **新专名符合「西方中世纪奇幻」命名原则**（见上文「命名原则」）
- [ ] **近期章节未擅自加入**「我」的订婚/联姻情节线、王室及政治高层直接接触（**提及**制度背景除外）
- [ ] **卷界**：卷一不含 Writ/北上；入学在 **卷二 · 7 岁**
- [ ] 未误改正文（除非用户明确要求）
- [ ] 滚动大纲：卷二及以后仍标 `【随剧情补充】` 处不强行定稿

---

## 开写顺序建议

1. 确认卷一 序章–第一章 **bible** 节拍无误
2. 开 **正文对话**（任意 Agent），写 `drafts/prologue.md` 或 `drafts/chapter-001.md`
3. 你审阅 → 文风问题在正文对话改，设定问题回 bible 对话
4. 序章满意并 **定稿** 后，继续下一章（@ 上一章正文）

---

## 常见误操作

| 误操作 | 后果 | 正确做法 |
|--------|------|----------|
| 正文对话里改 outline | bible 与正文两套版本 | 回 bible 对话改设定，再对齐正文 |
| 自动改 `finalized/` | 定稿被覆盖 | **仅**用户说「章节定稿」时才复制入库 |
| 设定对话里写正文 | 易忽略 preview / skill 自检 | 正文单独对话，@ style-guide + skill |
| 预览正文去 chapters/ 找 | 目录已迁 | **优先** `drafts/chapter-NNN.md` |
| 正文时未 @ writing-essentials / style-guide | 文风漂移 | 每次写章都 @ 要领 + style-guide |
| 用户说「全文」却改了别章 | 范围越界 | 默认只改**当前章**，他章须点名 |
