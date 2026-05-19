---
name: drama-team
description: 短剧编剧全流程系统 — 严格按集串行生成，含剧集连续性追踪、伏笔管理、视觉一致性管控与独立审核机制
version: 3.5
author: Hermes Agent + User
license: MIT
metadata:
  hermes:
    tags: [Short-Drama, Scriptwriting, Creative-AI, Visual-Consistency, Continuity, Foreshadowing, Sequential-Generation]
    related_skills: [hermes-agent, writing-plans, novel-to-short-drama-adaptation, short-drama-production-index]
---

# Hermes Agent 短剧编剧团队 v3.3

> 短剧编剧全流程系统：从小说/Idea到剧本、分镜、AI生图Prompt。
> **v3.0**: 审核员已内置（三视角定性 + 三Aligner定量），本技能是唯一来源。

### 🔥 批量任务执行纪律（v3.1 ⭐ 2026-05-15 Carmilla v2 教训）

> **用户原话**："升级前你先计划一下会怎么用技能进行生成分镜等信息"
> **教训**：不要接到"生成分镜"就立刻开进程跑。必须先停下来规划：用什么方式（主模型逐集/本地API/子代理）、预计耗时、质量预期，然后告诉用户确认后再执行。
> **强制规则**：涉及 10+ 集的批量生成分镜/Prompts 时，先输出执行计划（方式+预估时间+分批策略），等用户确认后再动手。

### 🔥 数据提取策略（v3.1 ⭐ 2026-05-15 Carmilla v2 教训）

> **用户原话**："提取数据或者什么转化过程出现问题，让大模型帮忙提取转化，准确性更高"
> **教训**：当正则/脚本解析好莱坞剧本出问题（角色名混入集标题、对白混入动作描述），不要反复调正则。直接让大模型（主模型）逐集读取剧本，输出结构化 JSON——它理解上下文，能区分"角色名"和"集标题"、"对白"和"动作描述"。
> **适用场景**：剧本 → 结构化 JSON 提取（角色、对白、场景）、复杂格式转换、跨版本 diff 分析。
> **硬编码正则的坑**（v3.1 实测 3 轮才调通）：
> 1. 角色名正则 `^[A-Z][A-Z0-9\s\.\'\-()]*$` 会捕获集标题（THE CURSE REVEALED、AFTERMATH）
> 2. 对白收集需要分离角色名后的"对白行"vs"动作描述行"（动作通常以人名+动词开头如 "Irina slams"）
> 3. 场景头正则 `INT.|EXT.` 需要 `$` 锚点否则匹配到中间行
> 4. `normalize_char` 需要处理 `(CONT'D)` 和 `(V.O.)` 后缀
> 5. 对白中的剧本术语（INSERT、SUPERIMPOSE、MATCH CUT TO）需要后处理清理

### 🔥 剧本提取：质量优先（v3.3 ⭐ 2026-05-15 Carmilla v2 教训）

> **用户原话**："就你自己一集一集分析提取，我们要高质量"
> **教训**：正则提取对白持续失败（动作描述混入对白、V.O.混淆、CONT'D归并失败、多行拼接断裂）。主模型逐集精读，对白/VO/Cliffhanger 准确无误，每集 30 秒，33 集一次完成。
> **强制规则**：剧本对白、V.O.、Cliffhanger 提取 **只用主模型逐集精读**，不调正则脚本，不让子代理跑。

> **实测数据**：本地 qwen27b-awq（port 8000）串行 16 批（每批 2 集）LLM 分镜生成，300 秒超时后才完成 0 集。
> **根因**：每集需要 1 次 HTTP 请求 + 模型推理 30-60 秒 + 上下文传输。32 集 × 30 秒 = 16 分钟，超时。
> **强制规则**：32 集以上的批量分镜/Prompts 生成，**不要用本地模型 API 循环调用**。改用主模型逐集直接写（write_file 模式），主模型已加载上下文，无需 HTTP 开销。
> **例外**：单集精修（1-2 集）可以用子代理或本地 API，但超过 5 集必须切主模型。

### 子 Agent 委托策略（v2.6 ⭐ 2026-05-12 Lady Audley's Secret 验证）

> **核心缺陷修复**：一次性委托 24+ 集给子 Agent 导致 token 耗尽/中断/跳过审核。
> **v3.5 升级（2026-05-15 Carmilla 验证）**：用户明确纠正"不要开子任务去做，你就主任务做完它"——子代理用于纯文本写作（剧本/分镜/Prompts/Review）必断。

### 🔥 硬规则：剧本/分镜/Prompts/Review 生成，主模型直接写（v3.5 ⭐）

| 任务类型 | 策略 | 理由 |
|----------|------|------|
| **剧本生成** | 主模型 write_file | 上下文已加载，直接写 |
| **分镜生成** | 主模型 write_file | 2-3集合并写入最佳（见下方批量模式） |
| **Prompts 生成** | 主模型 write_file | 纯文本写入，子代理 overhead 大 |
| **Review 审核** | 主模型直接做 | 多集审查子代理必超时 |
| **单集精修补遗** | 主模型 write_file | 1 集也要主模型做，子代理不值得启动开销 |
| **读者评审** | 主模型内联审查 | 多集采样+内联报告 |

### 子代理唯一适用场景
- **代码脚本编写**（generate_index.py, build_html.py, fix_prompts.py）
- **视频生成任务**（Dreamina/Seedance API 调用，可异步+notify）
- **独立推理任务**（单集质量分析、竞品对标）

### 🔥 批量 Prompts/Review 生成模式（v3.5 ⭐ 2026-05-15 Carmilla EP-10~30 验证）

**Prompts 批量写入**：主模型逐集 write_file，每集 1 次调用。EP-24~30（7集 Prompts）7 次 write_file 完成，每次 5-7K chars。
**Review 批量写入**：主模型用 `execute_code` 构造 Python 字典（所有集 Review 内容），一次性 write_file 全部。EP-10/13~30（19集 Review）单次 execute_code 完成，总耗时 12 秒 vs 逐集 write_file 预计 20+ 秒。

```python
# Review 批量模式（推荐 ⭐ — 19集 12秒完成）
from hermes_tools import write_file

reviews = {
    '10': '# EP-10 Review: ...\n## Episode Review — Score: 93/100 ✅\n...',
    '13': '# EP-13 Review: ...\n## Episode Review — Score: 92/100 ✅\n...',
    # ... 所有集
}

for ep, content in reviews.items():
    write_file(f"review/EP-{ep}.md", content)

# Prompts 批量模式 — 逐集 write_file（每集需要独立上下文推理）
# for ep in ['24','25','26','27','28','29','30']:
#     read_file(f"storyboard/EP-{ep}.md")  # 先读分镜
#     write_file(f"prompts/EP-{ep}.md", generated_content)  # 再写 Prompt
```

**选择依据**：
| 任务 | 推荐模式 | 理由 |
|------|---------|------|
| Prompts | 逐集 write_file | 需要逐集读分镜+独立推理，不适合字典构造 |
| Review | execute_code 字典批量 | 可先全部读取分镜到内存，再批量生成+写入 |

### 失败模式（Lady Audley's Secret 实测）

| 方案 | 结果 | 根因 |
|------|------|------|
| 一次委托 EP-06→30（24集） | EP-06 Prompts 就断 | 输入 152K tokens，输出预算只剩 ~6K，跑不完 |
| 一次委托 EP-07+08（2集） | 读了文件就断 | 上下文文件过多（6个文件 30K+），输出预算不够 |
| **主 Agent 自己逐集跑（推荐）** | ✅ EP-07 完整通过 | 主 Agent 已在上下文中，无需额外加载文件，输出空间充足 |

### 推荐策略

| 场景 | 策略 | 理由 |
|------|------|------|
| **单集精修**（推荐 ⭐） | 主 Agent 自己执行 | 上下文已加载，输出空间大，审核可控 |
| **补遗/补文件** | 子 Agent 委托（1集） | 如补 EP-06 Prompts（其他集已存在） |
| **读者评审** | 子 Agent 委托（1次/3-5集） | 独立视角，不影响主流程 |
| **批量初稿** | 子 Agent 可试（最多3集） | 接受质量较低，后续逐集精修 |

### 子 Agent 委托时上下文压缩

如果必须用子 Agent，压缩上下文：
```
# 坏（30K+ tokens）
- 读 outline.md 全文
- 读 characters.md 全文
- 读 manifest.md 全文
- 读 scene_prop_data.json 全文
- 读 script/EP-06.md 全文
- 读 storyboard/EP-06.md 全文
- 读 continuity.md 全文

# 好（~5K tokens）
- 读 continuity.md（核心，含进度+伏笔+角色状态）
- 读 outline.md 中对应集梗概（只读相关段落）
- 读 characters.md 中本集出场角色的 base_prompt（只读相关角色）
- 读 manifest.md 中的色调规则（当前集所在幕）
```

### 硬性规则（v2.6 新增）

1. **审核不可跳过** — 每集三件套完成后必须跑 Aligner 审核，≥80分才过。子 Agent 跳过审核 = 重来。质量基线稳定后（3+集通过）可接受1轮快速审核。
2. **每集输出预算** — 一集完整三件套 + 审核 ≈ 15-17K tokens 输出（含 continuity 更新）。子 Agent 总输出预算通常 20-30K，最多跑 1-2 集。
3. **主 Agent 逐集是默认方案** — 除非有明确理由（并行读者评审、补遗），否则主 Agent 自己跑质量更高。实测 20+集无问题。
4. **中断恢复** — 子 Agent 中断后，用 `ls script/ storyboard/ prompts/` + `stat` 时间戳确认实际完成到哪，不要假设。
5. **连续性文件批量更新** — continuity.md 不必每集更新，每 3-5 集批量更新一次即可。EP-20+ 后只保留活跃伏笔（已回收的压缩为一句话），避免上下文膨胀。
6. **Review 可内联** — 审核结果可内联到 Script 文件末尾（不单独写 review 文件），节省 1 个 write_file 调用。

## 核心问题

传统 AI 短剧创作存在五大问题：
1. **节奏/爽点/付费转化** — 缺乏对短剧特有规律的理解
2. **跨集叙事断裂** — 多子Agent并行生成时，EP-03不知道EP-02的悬念、角色状态、伏笔，导致剧情不连贯
3. **跨集视觉不一致** — 角色服装、道具、场景在AI生图时漂移
4. **编剧自批** — 缺乏独立审核，质量问题到生图阶段才发现
5. **伏笔无追踪** — 埋下的线索无人回收，"紫色咬痕"在EP-03出现，EP-10还是没解释

## 解决方案架构

### Agent 角色分工

| Agent | 职责 |
|-------|------|
| **主编剧** (主 Agent) | 严格按集串行创作剧本、分镜、AI Prompts |
| **视觉导演** (Visual Director) | 创建视觉资产清单，定义角色外观、服装、道具、场景的统一视觉规范 |
| **Aligner 系统** | 按内容类型路由到专用审核员：Script-Aligner（剧本）、Storyboard-Aligner（分镜）、Prompt-Aligner（Prompts），返回 PASS/FAIL。详见本技能 `## 审核员系统（三视角定性 + 三Aligner定量）` 章节 |

### 核心机制

1. **🔥 严格按集串行生成（v2.4 重大变更）** — 不使用多子Agent并行。主Agent逐集完成：EP-01剧本→审核→分镜→Prompts→提取连续性信息→EP-02...。避免会话隔离导致的叙事断裂。
2. **🔥 连续性追踪文件 `continuity.md`（v2.4 新增）** — 每集完成后自动更新，记录伏笔、悬念、角色状态变化，下一集开始前强制读取。
3. **六阶段创作流程** — 大纲 → 人物 → **视觉资产清单** → **按集循环（剧本→分镜→Prompts）**
4. **视觉资产驱动** — 所有 Prompts 强制注入视觉资产清单中的角色描述，确保跨集一致性
5. **ReAct 循环优化** — 按内容路由到对应 Aligner 审核（剧本→Script-Aligner，分镜→Storyboard-Aligner，含跨集连续性），不达标返回修改建议，循环直到通过
6. **文档驱动架构** — 所有内容分文件存储，支持断点续写

## 项目目录结构

```
project/
├── TASK.md                      # 任务进度跟踪
├── outline.md                   # 故事大纲
├── continuity.md                # 🔥 v2.4 剧集连续性追踪（伏笔/悬念/角色状态/交接记录）
├── characters/
│   └── characters.md            # 人物设定（性格、关系、动机、弧光）
├── visual_assets/
│   └── manifest.md              # 视觉规则（服装指南、表情库、色调/光影/构图）
├── scene_prop_data.json         # 场景/道具 Reference Prompts（AI生图参考图）
├── script/
│   └── EP-XX.md                 # 各集剧本
├── storyboard/
│   └── EP-XX.md                 # 各集分镜
├── prompts/
│   └── EP-XX.md                 # 各集 AI Prompts（含视觉资产注入）
├── generate_index.py            # MD → JSON 解析脚本
├── build_html.py                # JSON → SPA 工作台
├── project_data.json            # 结构化数据（工作台数据源）
├── index.html                   # 离线工作台页面
└── script.progress.md           # 创作进度记录
```

## 六阶段工作流（v2.4 — 按集串行 ⭐）

```
┌──────────┐    ┌──────────┐    ┌──────────────┐
│ 1.大纲   │ →  │ 2.人物   │ →  │ 3.视觉资产   │  ← 全局阶段（只跑一次）
│ (大纲)   │    │ (性格)   │    │ (外观规范)   │
└──────────┘    └──────────┘    └──────────────┘
     ✅            ✅               ✅
  人工确认      人工确认        人工确认（关键）

         ↓
    ┌───────────────────────────────────────────────────────────┐
    │              🔥 按集循环（串行，不是并行！）                │
    │                                                           │
    │  对 EP-01 → EP-02 → ... → EP-N 依次执行：               │
    │                                                           │
    │  ┌────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
    │  │ 4.剧本 │→ │ 5.分镜   │→ │ 6.Prompts │→│ 7.更新连续性│ │
    │  │        │  │          │  │          │  │ 文件        │ │
    │  └────────┘  └──────────┘  └──────────┘  └────────────┘ │
    │     ↓               ↓            ↓                       │
    │ Script-Aligner  Storyboard-Aligner  Prompts-审核          │
    │ (故事/逻辑)     (节奏/运镜/AI)   (视觉一致性)              │
    │                                                           │
    │  ⚠️ 上一集未通过审核 → 不进入下一集                        │
    │  ⚠️ 每集开始前必须读取 continuity.md                       │
    │  ⚠️ 每集结束后必须更新 continuity.md                       │
    └───────────────────────────────────────────────────────────┘
```

### 🔥 v2.4 关键变更：按集串行，不再并行

**为什么必须串行？**（2026-05-10 验证结论）

多子Agent并行生成（如 delegate_task 同时生成 EP-01~EP-05）的致命缺陷：
- **会话隔离** — EP-03 的 Agent 不知道 EP-02 发生了什么
- **悬念丢失** — EP-02 结尾的 Cliffhanger 在 EP-03 开头没有被回收
- **角色状态漂移** — EP-02 中主角受了重伤，EP-03 中已经活蹦乱跳
- **伏笔无人回收** — EP-01 埋的线索到了 EP-10 还没有人提
- **冲突模式重复** — 没有"上一集做了什么"的记忆，容易重复同样的冲突套路

**串行生成的优势：**
- 同一个 Agent 会话，完整上下文记忆
- 每集可以精确承接上一集的悬念和情绪
- 伏笔埋下后有追踪，确保后续回收
- 冲突模式自然升级（因为知道之前用过什么）

### 阶段 4-6（v2.4 — 按集串行循环 ⭐ 核心变更）

> **不再批量生成！** 改为逐集精雕：EP-01 三件套 + Aligner 审核 → 更新连续性文件 → EP-02 三件套 + 审核 → ...

**每集执行流程：**

```
┌─────────────────────────────────────────────────────────────────┐
│  for EP in [EP-01, EP-02, ..., EP-N]:                          │
│                                                                 │
│  Step 0: 读取上下文                                              │
│    - 读 continuity.md（上一集悬念、伏笔状态、角色状态）             │
│    - 读 outline.md 中对应集的分集梗概                             │
│    - 读 上一集 script/EP-XX.md 的结尾（特别是 Cliffhanger）        │
│                                                                 │
│  Step 1: 编剧 → script/EP-XX.md                                  │
│    - 必须回收上一集结尾悬念（开篇 3 秒）                           │
│    - 必须有新的冲突升级                                           │
│    - 必须处理到期伏笔（检查 continuity.md 中 due_episode）         │
│    - 结尾 Cliffhanger 标注钩子类型+等级（Hook: [类型+等级]）        │
│    - 可以埋新伏笔                                                 │
│                                                                 │
│  Step 2: Aligner 审核（含跨集连续性）                              │
│    - 新增检查：是否回收了上一集 Cliffhanger？                     │
│    - 新增检查：是否处理了到期伏笔？                               │
│    - 新增检查：冲突模式是否与上集重复？                           │
│    - FAIL → 重写 → 再审核（最多 3 轮，否则人工介入）              │
│                                                                 │
│  Step 3: 分镜 → storyboard/EP-XX.md                              │
│    - 同上 Aligner 审核                                           │
│                                                                 │
│  Step 4: Prompts → prompts/EP-XX.md                              │
│    - 同上 Aligner 审核                                           │
│                                                                 │
│  Step 5: 更新 continuity.md                                       │
│    - 记录本集新埋伏笔                                             │
│    - 标记本集回收的伏笔                                           │
│    - 更新角色状态变化                                             │
│    - 记录本集结尾 Cliffhanger + 钩子类型/等级                      │
│    - 记录本集钩子等级是否达标（用于复盘）                          │
│                                                                 │
│  → 进入下一集                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 🔥 continuity.md — 剧集连续性追踪文件

> **这是 v2.4 最核心的新增文件。** 它是连接集与集之间的"叙事记忆"，确保每一集都知道之前的故事状态。

**文件格式：**

```markdown
# 剧集连续性追踪 (Continuity Tracker)

> 自动生成，每集更新。下一集编剧开始前必须读取此文件。

---

## 当前进度
- **已完成**: EP-01, EP-02
- **进行中**: EP-03
- **总集数**: 12 集

---

## 伏笔管理 (Foreshadowing)

| ID | 描述 | 埋入集 | 计划回收集 | 状态 | 备注 |
|----|------|--------|-----------|------|------|
| F-01 | Laura颈间紫色咬痕发光 | EP-01 | EP-04 | 🟡 待回收 | 与Carmilla的吸血鬼身份相关 |
| F-02 | 父亲撕毁的名册关键页 | EP-03 | EP-06-07 | 🔵 已埋 | 涉及秘密社团名单 |
| F-03 | 老仆人可疑的眼神 | EP-02 | ? | 🟠 未定 | 可能是卧底 |
| F-04 | 地下室的钟声 | EP-01 | EP-05 | ✅ 已回收 (EP-03) | 已确认是密室机关 |

---

## 上一集结尾 (Last Cliffhanger)

### EP-02 结尾
- **Hook**: 危险钩子(3) + 异常钩子(2)
- **描述**: Carmilla化为雾气消失，Laura颈间的咬痕开始发出紫色光芒。
  Laura对着空房间说："你到底是谁？"

**下一集（EP-03）必须：**
1. 开篇直接承接：Laura触摸发光的咬痕
2. 揭示或推进：紫光与Carmilla的联系
3. 建立新的悬念（目标≥4级）

---

## 角色当前状态 (Character State)

| 角色 | 当前状态 | 变化时间 |
|------|---------|---------|
| Laura | 颈间有紫色发光咬痕，恐惧但开始调查 | EP-01至今 |
| Carmilla | 身份神秘，已吸血一次，表现出矛盾情感 | EP-02 |
| 父亲 | 发现女儿异常，开始怀疑 | EP-03 |
| 老仆人 | 行为可疑，暗中观察Laura | EP-02 |

## 角色互动记录 (v5.1 ⭐ 新增)

| 集数 | 互动角色 | 互动类型 | 情感基调 |
|------|---------|---------|---------|
| EP-01 | Laura × Carmilla | 初遇+吸血 | 恐惧 |
| EP-02 | Laura × Carmilla | 触摸+威胁 | 危险暧昧 |
| ... | ... | ... | ... |

> 用途：Aligner 检查"原谅/和解是否有前置互动铺垫"时参考

## 感官刺激记录 (v5.1 ⭐ 新增)

| 集数 | 视觉动作 | 物理亲密 | 超自然现象 | 危险场景 | 感官得分(0-4) |
|------|---------|---------|-----------|---------|--------------|
| EP-01 | ✅紫纹特写 | ❌ | ✅Carmilla化雾 | ✅7天倒计时 | 3 |
| EP-02 | ❌ | ✅摸下颌线 | ❌ | ✅被困 | 2 |
| EP-03 | ❌ | ❌ | ❌ | ❌ | 0 ⚠️ |
| ... | ... | ... | ... | ... | ... |

> 用途：Aligner 检查"连续低密度集"和"单集感官刺激"时参考

---

## 冲突模式记录 (Conflict Pattern Log)

| 集数 | 冲突类型 | 具体表现 |
|------|---------|---------|
| EP-01 | 超自然入侵 | 吸血鬼咬人 |
| EP-02 | 身份谜团 | Carmilla现身+消失 |
| EP-03 | 信息争夺 | 父亲撕毁名册 |

**⚠️ 下一集（EP-04）应避免重复以上冲突类型，可考虑：情感对峙 / 外部威胁 / 信任背叛**

---

## 未解决问题 (Open Questions)

1. Carmilla 为什么选择 Laura？（计划 EP-05 揭示）
2. 名册上记录了什么秘密社团？（计划 EP-06-07）
3. 老仆人是否知道 Carmilla 的身份？（待观察）
4. 紫色光芒是诅咒还是礼物？（计划 EP-04 推进）
```

**更新规则（每集完成后执行）：**

1. **伏笔管理表** — 新增本集埋下的伏笔，标记本集回收的伏笔
2. **Last Cliffhanger** — 记录本集结尾悬念，标注下一集必须承接的内容
3. **角色状态** — 更新因本集剧情发生变化的角色状态
4. **冲突模式** — 记录本集冲突类型，供下一集参考（避免重复）
5. **未解决问题** — 更新问题列表，调整回收计划

**编剧读取规则（每集开始前执行）：**

1. 必须读取 `continuity.md` 全文
2. 检查伏笔表：是否有伏笔的 `due_episode` = 当前集？→ 必须处理
3. 检查 Last Cliffhanger：上一集悬念 → 必须在开篇回收
4. 检查冲突模式：避免与最近 2 集使用相同冲突类型
5. 检查角色状态：确保角色行为符合当前状态

### 🔥 上下文长度管理（v2.5 ⭐ 新增）

> **核心缺陷修复**：随着集数增加，continuity.md 越长越大，EP-15+ 时上下文可能超过 AI 限制。需要智能截断。

**截断策略（当 continuity.md > 6000 字符时触发）：**

```
优先级（高→低，高优先级保留，低优先级截断）：

1. 【必须保留】
   - 当前进度（5行）
   - Last Cliffhanger（完整）— 这是下一集必须回收的内容
   - 伏笔管理表 — 只保留状态为"🟡 待回收"和"🔵 已埋"的行
   - 角色当前状态（完整）— 这是行为一致性的基础

2. 【精简保留】
   - 冲突模式记录 — 只保留最近 3 集（避免重复需要最近参考）
   - 未解决问题 — 保留，但每个问题压缩到一句话

3. 【可截断】
   - 已回收的伏笔（✅ 已回收）— 只保留 ID + 一句话摘要
   - 超过 5 集前的冲突模式 — 删除
```

**AI 摘要化方案（当截断后仍超过 8000 字符）：**
- 调用 AI 对连续性文件做摘要压缩到 3000 字
- 摘要指令：`将以下连续性文件压缩到3000字以内，保留：当前进度、Last Cliffhanger完整内容、未回收伏笔、角色状态、最近3集冲突模式`
- 摘要版本存储为 `continuity_summary.md`（轻量版），全量保留 `continuity.md`（完整历史）

**编剧调用规则：**
- EP-10 之前：读 `continuity.md` 全文
- EP-10 之后：优先读 `continuity_summary.md`（如存在），否则读截断后的 `continuity.md`
- 无论哪种，都必须同时读上一集 `script/EP-XX.md` 的完整 Cliffhanger 部分

### 🔥 读者反馈模拟（v2.5 ⭐ 新增）

> **核心缺陷修复**：Aligner 是 AI 审核，缺少"目标观众视角"。短剧的核心是爽点和付费转化，需要模拟真实用户反应。

> **v3.1 关键教训（2026-05-14 基督山伯爵验证）**：
> 多集审查（15+集）用子 Agent 必超时/中断。主 Agent 直接做审查是唯一可行方案。
> 审查结果 → 修改闭环：审查报告写文件 → 根据报告逐集 patch/write。

**主 Agent 审查工作流（推荐 ⭐ v3.1 新增）：**

```
Step 1: 采样关键集（不读全25集，只读关键部分）
  - head -6 + tail -10 每集剧本（获取结构+关键对白）
  - grep 关键道具/伏笔（验证一致性）
  - 采样 prompts 验证AI生图可行性（1-3集代表）

Step 2: 直接产出三视角审查报告（内联，不委派）
  - 急躁哥：节奏/留存（前5秒hook、爽点密度、拖沓集）
  - 逻辑控：时间线/动机链/道具回收/时代错误
  - 视听专家：多人同镜风险、文字道具、武器/戒指AI生成可行性

Step 3: 综合汇总 → 优先级分级
  - 🔴 必须修改（影响留存/逻辑硬伤）
  - 🟡 建议优化（提升体验）
  - 🟢 锦上添花（制作阶段处理）

Step 4: 逐集修改
  - 🔴 问题：用 patch 或 write_file 修改脚本
  - 🟡 问题：记录到制作检查清单（不改脚本，制作阶段处理）
  - 更新 TASK.md 标记修改完成
```

**审查报告输出格式（三文件 + 汇总）：**
```
REVIEW-IMPATIENT-BRO.md  — 急躁哥报告（节奏/爽点）
REVIEW-LOGIC-MASTER.md   — 逻辑控报告（时间线/逻辑）
REVIEW-VISUAL-EXPERT.md  — 视听专家报告（AI制作可行性）
REVIEW-SUMMARY.md        — 综合汇总（优先级+修改清单）
```

**审查重点关注项（US/EU 市场 ⭐ v3.1）：**
- **前5秒hook**：开场纯风景 > 5秒 = 必改。直接上冲突。
- **拖沓集检测**：连续3集"主角倒霉"或纯文戏 → 观众流失。至少隔1集有冲突升级。
- **时间跳跃标记**：>3年跳跃必须加 "X YEARS LATER" 标题卡。
- **时代错误**：电话(1838年不存在)、电报(1837年刚发明，马赛→巴黎不可靠)。改为信使/骑手。
- **地理跳跃**：单集内跨城市/国家 → 需加过渡（马车/船只场景）或改为闪回。
- **逻辑闭环**：复仇集数 = 仇人数（1:1），不能说"三分之一"当三个仇人已灭。

> **子 Agent 审查失败模式（实测）：**
> | 方案 | 结果 | 根因 |
> |------|------|------|
> | 子 Agent 读25集剧本做审查 | 600s 超时/中断 | 输入 150K+ tokens，分析输出空间不足 |
> | 子 Agent 只读关键集（10集） | 仍可能中断 | 审查需要上下文对比，采样不完整导致结论浅 |
> | **主 Agent 内联审查（推荐）** | ✅ 完整报告 | 上下文已加载，无需额外 token |

### 🔥 质量控制与回退机制（v2.5 ⭐ 新增）

> **核心缺陷修复**：缺少"退出一集"的机制，发现重大逻辑错误后不知道如何修复后续剧集。

**质量门禁（每个阶段通过标准）：**

| 阶段 | 质量门 | 未通过的处理 |
|------|--------|-------------|
| 大纲 | 人工确认 | 重写大纲 |
| 人物 | 人工确认 | 调整角色设定 |
| 视觉资产 | 人工确认 | 调整视觉规范 |
| 剧本 | Aligner ≥ 80 | 重写剧本（最多3轮） |
| 分镜 | Aligner ≥ 80 | 重写分镜（最多3轮） |
| Prompts | Aligner ≥ 80 | 重写 Prompts（最多3轮） |
| 读者评审 | 无硬伤 | 根据建议优化 |

**回退链机制（发现前集有重大逻辑错误时）：**

```
发现 EP-03 有逻辑错误，但 EP-04/EP-05 已经完成：

Step 1: 修复 EP-03
  - 修改 script/EP-03.md
  - 重新对齐 Aligner
  
Step 2: 更新 continuity.md
  - 更新 EP-03 的 Cliffhanger
  - 更新角色状态变化
  - 更新伏笔表（如果有变更）
  
Step 3: 级联回退
  - EP-04: 读取新的 continuity.md → 检查是否需要修改
  - EP-05: 同上
  - 使用"差异检测"：对比修改前/后的 continuity.md，
    找出受影响的集数（只回退真正受影响的集，不是全部）
    
Step 4: 标记已回退
  - 在 TASK.md 中标记：EP-03 → 回退修复 → EP-04/EP-05 已同步
```

**回退触发条件：**
- 人工发现前集有重大逻辑错误
- 读者评审发现前集有硬伤
- 后续集无法衔接前集内容（如角色状态不一致）

**爽点密度统计（每 5 集输出一次）：**

```markdown
## 爽点统计 (EP-01 ~ EP-05)

| 集数 | 爽点类型 | 数量 | 密度（秒/爽点） |
|------|---------|------|----------------|
| EP-01 | 反转 | 2 | 35s |
| EP-02 | 打脸 | 1 | 70s |
| EP-03 | 复仇 | 3 | 23s |
| EP-04 | 悬念 | 2 | 35s |
| EP-05 | 反转+打脸 | 3 | 23s |

⚠️ 警告：EP-02 爽点密度过低（70s/个），建议在下集补偿
```

### 🔥 视觉资产变更检测（v2.5 ⭐ 新增）

> **核心缺陷修复**：长剧（30+集）后期，新角色/场景/道具不断出现，视觉资产与剧情不同步。

**变更触发条件（每集剧本完成后检查）：**

```
触发条件 → 操作：

1. 剧本出现新角色名（不在 characters.md 中）
   → 暂停 → 补充 characters.md + manifest.md → 继续

2. 剧本出现新场景（不在 scene_prop_data.json 中）
   → 暂停 → 补充 scene_prop_data.json + manifest.md → 继续

3. 剧本出现新关键道具（不在 scene_prop_data.json 中）
   → 暂停 → 补充 scene_prop_data.json → 继续

4. 角色服装发生重大变化（如入狱→出狱）
   → 暂停 → 更新 manifest.md 服装指南 → 继续
```

**自动化检测方法：**

```python
# 伪代码：检测新角色
import re

known_chars = set()  # 从 characters.md 提取
new_chars = set()

for line in script_lines:
    # 提取对话角色名
    for match in re.finditer(r'^([A-Z][A-Z ]*):', line):
        name = match.group(1).strip()
        if name not in known_chars and name not in ['NARRATOR', 'VOICEOVER']:
            new_chars.add(name)

if new_chars:
    print(f"⚠️ 发现新角色：{new_chars}")
    print("→ 请更新 characters.md + manifest.md")
```

**视觉资产维护检查清单（每 5 集执行一次）：**

- [ ] characters.md 中所有角色都还在剧情中？（移除退场角色或标记"已退场"）
- [ ] manifest.md 服装指南是否覆盖当前剧情阶段？
- [ ] scene_prop_data.json 场景是否覆盖当前使用的场景？
- [ ] 色调规则是否需要调整？（如从"冷蓝灰"过渡到"暖金色"）

### 🔥 串行 vs 并行的明确划分（v2.5 ⭐ 新增）

> **核心缺陷修复**：不是所有阶段都必须串行。某些阶段可以并行以提高效率。

**必须串行的阶段：**

| 阶段 | 原因 |
|------|------|
| 剧本（script） | 每集依赖上一集的 Cliffhanger 和连续性 |
| 大纲（outline） | 全局性，必须人工确认后进入下一阶段 |
| 人物（characters） | 全局性，影响后续所有集 |
| 视觉资产（visual_assets） | 全局性，影响所有 Prompts |

**可以并行的阶段：**

| 阶段 | 并行方式 | 前提条件 |
|------|---------|---------|
| 分镜（storyboard） | 如果剧本已全量完成，可以并行写分镜 | 剧本全部 Aligner PASS |
| Prompts | 如果分镜已全量完成，可以并行写 Prompts | 分镜全部 Aligner PASS |
| 读者评审 | 可以与剧本并行（评审已完成的集） | 至少 3 集已完成 |
| 生图（image_gen） | 多账号并行 | Prompts 已完成 |
| 视频生成（video_gen） | 多账号并行 | 图片已生成 |

**推荐工作流（效率 vs 质量平衡）：**

```
方案 A：全量串行（质量最高）
  大纲 → 人物 → 视觉资产 → 
  EP-01(剧本→分镜→Prompts) → EP-02(剧本→分镜→Prompts) → ...
  优点：质量最高，连续性最好
  缺点：速度慢

方案 B：剧本串行 + 分镜/Prompts 批量（推荐 ⭐）
  大纲 → 人物 → 视觉资产 →
  剧本：EP-01 → EP-02 → ... → EP-N（串行）
  ↓
  分镜：EP-01 ~ EP-N（批量并行）
  ↓
  Prompts：EP-01 ~ EP-N（批量并行）
  优点：剧本质量高，分镜/Prompts 效率高
  缺点：分镜/Prompts 的连续性略弱

方案 C：全量并行（速度最快）
  大纲 → 人物 → 视觉资产 →
  EP-01 ~ EP-N 同时生成（不推荐 ⚠️）
  优点：速度最快
  缺点：连续性差，质量低

方案 D：单集三件套并行（v3.0 ⭐ 2026-05-14 基督山伯爵验证）
  适用条件：已有多集上下文（EP-XX 已完成），补遗最后 1-3 集
  方式：用 delegate_task 同时派 3 个子 Agent 生成 script + storyboard + prompts
  关键：上下文压缩到 ~5K tokens（见下方"子 Agent 委托时上下文压缩"）
  优点：单集三件套 ~2.5 分钟完成（vs 串行 ~7.5 分钟）
  缺点：需要严格的上下文压缩，不适合前 5 集
  验证：Count of Monte Cristo EP-24+EP-25，3 个子 Agent 并行，152s 完成
  注意：生成后必须做文件验证（见下方"生成后验证"）
```

**子 Agent 并行时上下文压缩（v3.0 ⭐ 关键）：**

```
# 坏（30K+ tokens，导致子 Agent 断掉）
- 读 outline.md 全文
- 读 characters.md 全文
- 读 manifest.md 全文
- 读 scene_prop_data.json 全文
- 读 script/EP-XX.md 全文
- 读 storyboard/EP-XX.md 全文
- 读 continuity.md 全文

# 好（~5K tokens，验证成功）
- 读 continuity.md（核心，含进度+伏笔+角色状态）
- 读 outline.md 中对应集梗概（只读相关段落）
- 读 characters.md 中本集出场角色的 base_prompt（只读相关角色）
- 读 manifest.md 中的色调规则（当前集所在幕）
- 提供上一集 script 结尾钩子（100-200字摘要）
- 提供分镜/Prompts 格式参考（描述格式，不读全文件）
```

**生成后验证（v3.0 ⭐ 必做）：**

```python
# 每次批量生成后立即运行
import os
base = "/path/to/project"
for i in range(1, TOTAL_EPS + 1):
    ep = f"EP-{i:02d}"
    for subdir in ["script", "storyboard", "prompts"]:
        fp = f"{base}/{subdir}/{ep}.md"
        if not os.path.exists(fp):
            print(f"MISSING: {subdir}/{ep}.md")
        else:
            # 验证非空（>500 bytes = 有内容）
            size = os.path.getsize(fp)
            if size < 500:
                print(f"SUSPECT: {subdir}/{ep}.md ({size} bytes, 可能为空)
```

**TASK.md 更新（v3.0 ⭐ 必做）：**
- 生成完成后必须更新 TASK.md 进度（✅ 标记完成的集）
- 更新项目状态（如 "Phase 2 全部完成"）
- 添加更新日志条目
- 不更新会导致下次续做时无法判断真实进度

### 🔥 时间预算管理（v2.5 ⭐ 新增）

> **核心缺陷修复**：每集 70 秒的硬性限制常被打破，后期合成时时间对不上。

**时间预算模板（每集编剧时必须遵守）：**

```
总时长：70s

预算分配：
├── 对白时间：35-40s（约 12-15 句 × 3s/句）
├── 纯动作时间：15-20s（开场 3s + 转场 + 结尾慢推）
├── 情感留白：5-8s（沉默/表情/反应镜头）
└── 转场/黑屏：2-5s

强制规则：
- 开场 3 秒：必须直接进入冲突（不能空镜铺垫）
- 结尾 5-10 秒：Cliffhanger 慢推（最长 10s）
- 单个镜头 ≤ 5s（悬念慢推除外）
```

**时间校验（编剧完成后自动检查）：**

```python
# 伪代码
total_time = sum(shot_duration for shot in shots)
assert abs(total_time - 70) <= 5, f"时间偏差过大：{total_time}s vs 70s"

dialogue_count = len([s for s in shots if s.get('dialogue')])
assert 12 <= dialogue_count <= 15, f"对白数量：{dialogue_count}（标准 12-15）"

max_shot = max(shots, key=lambda s: s['duration'])
assert max_shot['duration'] <= 10, f"镜头过长：{max_shot['duration']}s（最长 10s）"
```

**分镜时间校验（Storyboard 阶段）：**

| 集类型 | 镜头数 | 单镜平均 | 总时长 |
|--------|--------|---------|--------|
| 氛围集 | 16-18 | 3.9-4.4s | 70s |
| 标准集 | 18-22 | 3.2-3.9s | 70s |
| 恐怖集 | 20-24 | 2.9-3.5s | 70s |
| 高潮集 | 22-25 | 2.8-3.2s | 70s |

### 🔥 文件依赖关系图（v2.5 ⭐ 新增）

> **核心缺陷修复**：12+ 个文件，新手不知道改了哪个需要同步更新哪些。

**文件依赖关系：**

```
outline.md
  ├──→ characters.md（依赖大纲中的角色）
  │     ├──→ visual_assets/manifest.md（依赖角色设定）
  │     ├──→ scene_prop_data.json（依赖角色使用的场景/道具）
  │     └──→ script/EP-XX.md（依赖角色身份）
  │
  └──→ continuity.md（依赖大纲中的伏笔规划）
        └──→ script/EP-XX.md（依赖连续性信息）

visual_assets/manifest.md
  ├──→ prompts/EP-XX.md（依赖视觉规则）
  └──→ storyboard/EP-XX.md（依赖色调/光影）

scene_prop_data.json
  └──→ prompts/EP-XX.md（依赖场景/道具 Reference）

script/EP-XX.md
  ├──→ storyboard/EP-XX.md（依赖剧本内容）
  └──→ prompts/EP-XX.md（依赖剧本场景）

storyboard/EP-XX.md
  └──→ prompts/EP-XX.md（依赖分镜镜头）
```

**文件变更联动规则：**

| 修改了 | 必须同步更新 | 可选更新 |
|--------|-------------|---------|
| outline.md | continuity.md（伏笔规划） | characters.md（如果角色有变化） |
| characters.md | manifest.md（服装/表情） | scene_prop_data.json（如果新角色有新场景） |
| manifest.md | prompts/EP-XX.md | 无 |
| script/EP-XX.md | storyboard/EP-XX.md, prompts/EP-XX.md, continuity.md | 无 |
| storyboard/EP-XX.md | prompts/EP-XX.md | 无 |
| continuity.md | 下一集的 script/EP-XX.md | 无 |

---

### 阶段 0：输入处理（v2.5 ⭐ 新增）

> **核心缺陷修复**：用户输入形式多样（小说文本/PDF/Idea描述/灵感碎片），必须先标准化再进入大纲阶段。

**输入类型识别与处理策略：**

| 输入类型 | 处理方式 | 输出 |
|---------|---------|------|
| **完整小说**（文本/PDF） | 读全文 → 提取核心情节、角色、世界观 → 生成改编规划 | 改编规划 → 进入阶段1 |
| **小说片段/大纲** | 直接分析 → 补全缺失信息 → 生成改编规划 | 改编规划 → 进入阶段1 |
| **Idea描述**（文字/语音） | 澄清需求 → 扩写世界观 → 生成大纲草案 | 大纲草案 → 进入阶段1 |
| **灵感碎片**（图片/关键词） | 视觉分析 → 头脑风暴 → 生成Idea描述 | Idea描述 → 进入阶段1 |

**小说输入处理流程（最常见场景）：**

```
Step 0a: 读取输入
  - 文本/PDF → 提取全文
  - 判断类型：完整小说 / 章节片段 / 大纲
  
Step 0b: 内容分析
  - 提取核心角色（≥3个）
  - 提取主要冲突线
  - 提取世界观设定
  - 估算总字数 → 决定集数（每集70s ≈ 1000-1500字小说内容）
  
Step 0c: 改编规划
  - 确定改编策略（忠实原著 / 创意改编 / 大纲驱动）
  - 确定集数（12/24/36集）
  - 确定风格（哥特暗黑 / 甜宠 / 复仇 / 悬疑...）
  - 确定核心卖点（双女主 / 宿敌 / 禁忌之恋...）
  
Step 0d: 进入阶段1（大纲生成）
```

**Idea输入处理流程：**

```
Step 0a: 接收Idea（文字/语音转文本）
Step 0b: 澄清需求（如有缺失）
  - 风格？（哥特/甜宠/复仇...）
  - 集数？（12/24/36）
  - 核心关系？（双女主/宿敌...）
  - 结局类型？（HE/BE/开放）
Step 0c: 扩写世界观（世界观+设定+规则）
Step 0d: 生成大纲草案 → 进入阶段1
```

### 阶段 1-2：大纲 + 人物设定

标准流程 — 确定故事方向、核心角色、人物关系、结局类型。

**大纲标准结构（必须包含）：**
```markdown
# 故事大纲

## 三幕结构
### 第一幕：建立（EP-01 到 EP-N/3）
- 核心事件
- 角色建立
- 激励事件

### 第二幕：对抗（EP-N/3 到 EP-2N/3）
- 冲突升级节点
- 中段转折点
- 最低谷时刻

### 第三幕：解决（EP-2N/3 到 EP-N）
- 高潮构建
- 最终对决
- 结局（HE/BE/开放）

## 分集梗概
### EP-01: 标题
- 核心事件（1-2句）
- 爽点类型（复仇/打脸/反转...）
- 结尾悬念
### EP-02: 标题
...

## 伏笔规划表（v2.5 ⭐）
| ID | 描述 | 埋入集 | 回收集 | 重要性 |
|----|------|--------|--------|--------|
| F-01 | 紫色咬痕的秘密 | EP-01 | EP-04 | 🔴 核心 |
| F-02 | 名册上的名字 | EP-03 | EP-06-07 | 🟡 重要 |
```

### 阶段 3：视觉资产 — 三文件架构（v2.3 ⭐）

> **这是跨集视觉一致性的关键阶段。** 基于人物设定，创建三个职责单一的文件，后续所有 Prompts 必须引用这三份文件。

**三文件架构（单一职责原则）：**

```
characters.md          ← 角色是谁（性格、动机、弧光、关系）
scene_prop_data.json   ← 场景/道具 Reference Prompts（AI生图参考图）
manifest.md            ← 视觉规则（服装指南、表情库、色调/光影/构图）
```

**为什么三分离？**（2026-04-30 Count of Monte Cristo 项目验证）
- 旧版 manifest.md 塞了角色外观+场景描述+服装+道具 → 46KB 臃肿文件
- `characters.md` 已有角色外观，`scene_prop_data.json` 已有场景/道具 → manifest.md 大量重复
- 精简后 manifest.md 保留**不可替代的内容**：服装场景映射、表情关键词、色调/光影/构图规则 → 16KB
- 三文件互不重复，各司其职，维护清晰

**产出文件 1：`characters.md`**（同 v2.0，不变）

**产出文件 2：`scene_prop_data.json`**（v2.2 → v2.3 保持不变）

```json
{
  "scenes": [
    {
      "id": "S-01",
      "name": "Marseille Port Dock",
      "cn_name": "马赛港口码头",
      "prompt": "Gothic Korean manga style, 9:16 vertical, wide establishing shot, no characters, environmental scene reference, ...",
      "status": "pending"
    }
  ],
  "props": [
    {
      "id": "P-01",
      "name": "Iron Gate",
      "prompt": "Gothic Korean manga style, close-up still life, no characters, prop reference, ...",
      "status": "pending"
    }
  ]
}
```

**产出文件 3：`manifest.md`（精简版）**

```markdown
# 视觉资产清单 (Visual Asset Manifest)

> **用途**：全局视觉规则 + 服装指南 + 表情姿态库
> **角色外观** → 见 `characters.md`
> **场景/道具 Reference Prompts** → 见 `scene_prop_data.json`

---

## 场景引用速查（from scene_prop_data.json）

| ID | 场景名 | 中文名 |
|----|--------|--------|
| S-01 | Marseille Port Dock | 马赛港口码头 |
| ... | ... | ... |

> 完整 Reference Prompt 在 `scene_prop_data.json.scenes[].prompt`

---

## 道具引用速查（from scene_prop_data.json）

| ID | 道具名 |
|----|--------|
| P-01 | Iron Gate |
| ... | ... |

> 完整 Reference Prompt 在 `scene_prop_data.json.props[].prompt`

---

## 服装指南 (按角色×场景)

> 此部分是所有文件唯一来源。Prompt 中角色服装必须按此表匹配当前场景。

### [角色名]
| 阶段/场景 | 服装 |
|-----------|------|
| 入狱前 | 白色水手衬衫+蓝色裤子+棕色靴子 |
| 地牢 | 破碎棕色麻布囚服 |
| ... | ... |

---

## 表情/姿态关键词库

> 写 Prompt 时从对应角色选关键词，确保情绪准确。

### [角色名]
- **愤怒**：眉头紧锁、嘴唇紧抿、握拳
- **恐惧**：瞳孔放大、呼吸急促、后退
- ...

---

## 全局视觉规则 (Global Visual Rules)

### 色调规则 (Color Palette Rules)
| 情境 | 主色调 | 辅助色 |
|------|--------|--------|
| 入狱前（Ep1-2） | 金色暖光 | 蔚蓝, 纯白 |
| 地牢时期（Ep4-12） | 冷蓝灰 | 烛火橙黄, 铁锈红 |
| ... | ... | ... |

### 光影规则 / 构图规则 / 韩漫风格元素
（详见模板）

---

## 文件关系

```
characters.md          ← 角色是谁
scene_prop_data.json   ← 场景/道具 Reference Prompts
manifest.md (本文件)    ← 视觉规则（服装、表情、色调、光影、构图）
```

**Prompt 编写流程**：
1. `characters.md` → 确认角色身份
2. `scene_prop_data.json` → 取场景/道具 ID → `[ref: S-XX]` / `[ref: P-XX]`
3. `manifest.md` → 取服装（按场景）+ 表情（按情绪）
4. `manifest.md` → 取色调/光影/构图规则
```

**三文件创建顺序：**
1. 基于 `characters.md` → 视觉导演为每个角色写服装表 + 表情关键词
2. 遍历剧本场景头 → 提取唯一场景（去重后 ~10-15 个）→ 写 `scene_prop_data.json.scenes[]`
3. 识别关键道具 → 写 `scene_prop_data.json.props[]`
4. 编写 `manifest.md` → 场景/道具速查表 + 服装指南 + 表情库 + 全局规则
5. **人工确认** — 三文件必须经导演（用户）确认后进入剧本阶段

### 阶段 4-5：剧本 + 分镜

编剧完成三件套中的剧本和分镜，派独立 Aligner 审核。

### 阶段 6：AI Prompts（含视觉资产强制注入 ⭐）

> **每张图 Prompt 开头必须注入对应的角色外观描述（从 manifest.md 拉取）。**

**Prompts 模板：**

```markdown
# EP-XX: Title - AI Prompts

## Visual Asset References（从 manifest.md 拉取）
### 本集出场角色外观：
**Carmilla**: 哥特暗黑韩漫风格，175cm高挑女性吸血鬼，苍白肤色，及肩黑色微卷发，琥珀色瞳孔，尖牙，黑色长裙+银色项链
**Irina**: 哥特暗黑韩漫风格，22岁年轻女性，黑色直发及腰，深褐色瞳孔，白色衬衫+深色西装外套+百褶裙

### 本集场景：
**古堡卧室**: 哥特风格，石墙+烛台+天鹅绒窗帘，冷色调烛光照明

## Image Prompts (Dreamina) — [N] frames, one per shot
### Frame 1: [time] [shot_type]
**Prompt:** 哥特暗黑韩漫风格, 9:16 vertical, [shot_type], [action], 
[Carmilla: 苍白肤色, 及肩黑色微卷发, 琥珀色瞳孔, 黑色长裙+银色项链], 
[场景: 古堡卧室, 石墙+烛台, 冷色调烛光], [mood]

### Frame 2: ...

## Video Prompts (Seedance) — 每3-4个连续镜头合并为一段
### Shot [N]: [time_range]
**Prompt:** [action_sequence], camera [movement], [mood]
**Duration:** [N]s
```

**Prompt 注入规则：**
- 每张 frame prompt 开头 = 风格 + 画幅 + 角色外观描述 + 场景描述
- 角色外观描述**逐字复制**自 manifest.md，不可自由发挥
- 多角色同框时，每个角色的外观描述都要包含
- 新角色首次出场时，同时更新 manifest.md

### 帧级 Prompt 场景 + 道具批量注入（v2.1 ⭐ 2026-04-29 Carmilla 项目验证）

> **v3.2 升级（2026-05-15 导演反馈）**：
> - Image Prompt 中每个场景/道具引用后必须标注 `key props: [道具名]`，与 manifest 道具清单一致
> - Video Prompt 开头必须声明参考图：`@图片1: ep01/compressed/kf1_shot1_*.png`（Seedance 2.0 @语法）
> - 每个主要角色在 manifest.md 中必须有 3 视图 Prompt（front/side/back）
> - 全局资源（角色图/场景图/道具图）存 `visual_assets/`，分集资源（关键帧）存 `epXX/`

> 当剧本表格里所有行都只有 `S-01`（无场景名）时，帧 prompt 无法区分场景变化。需要**从动作描述推断场景切换**，并用**时间范围匹配**将帧映射到脚本行。

**场景推断规则（Action → Scene）：**
```
关键词映射示例：
"走廊" → 走廊 | "冲开门"/"打开门" → 走廊 | "走廊空" → 走廊空荡
"花园" → 花园 | "走出" → 城堡外 | "大厅" → 大厅
"书房" → 书房 | "楼梯" → 楼梯 | "厨房" → 厨房
"墓园" → 墓园 | "废墟" → 废墟 | "仪式" → 仪式室
```

**场景继承逻辑（关键！）：**
```
1. S-XX 带显式场景名（如 "S-01 Laura卧室"）→ 使用该场景，设为 prev_scene
2. S-XX 无显式名（如 "S-01"）→ 查 S-XX→name 映射表
   - 映射表有值 → 用映射值，但先用动作关键词检查是否场景切换
   - 映射表无值 → 从动作推断或继承 prev_scene
3. 一旦推断出场景变化，后续无关键词的行继承新场景
```

**时间匹配策略（不要用重叠面积！）：**
```
❌ 错误：用时间重叠面积匹配 → 大区间帧会匹配到前面的小区间脚本行
   例：Frame 53-57s 与脚本 46-50s 重叠4秒 > 与 55-58s 重叠2秒 → 选错场景

✅ 正确：用帧 start 时间距离脚本行 start 时间最近的匹配
   例：Frame 57-65s → 找 |57 - script_row.start| 最小的行 → 55-58s (dist=2)
   结果：正确匹配到走廊场景
```

**道具注入方法：**
```python
# 中文动作关键词 → 英文道具描述映射
PROP_KEYWORDS = {
    "镜子": "ornate antique full-length mirror with carved frame",
    "日记": "leather-bound diary with faded ink writing",
    "茶杯": "porcelain teacup on a wooden table",
    "照片": "old sepia-toned photograph in a silver frame",
    "匕首": "ornate silver dagger with engraved handle",
    "窗外": "tall Gothic arched window with moonlight streaming through",
    "脚印": "wet footprints on stone floor slowly evaporating",
    # ... 24+ props mapped
}

# 注入位置：scene 描述之后
# scene: [Gothic castle corridor, stone walls, ...], ornate silver dagger with engraved handle
```

**批量处理脚本模式：**
```
fix_prompts.py → parse_script_scenes() → match_frame_to_script() → fix_frame()
- parse_script_scenes: 解析脚本表格，建立 S-XX→name 映射 + 动作推断 + 场景继承
- match_frame_to_script: 按帧 start 时间最近匹配脚本行
- fix_frame: 替换 scene: [...] + 注入 props
- 正则：r'(### Frame (\\d+): ([\\d\\-]+s.*?)\\n\\*\\*Prompt:\\*\\*)(.*?)(?=\\n###|\\Z)'
```

**常见陷阱：**
- ❌ 帧时间含中文后缀（`46-50s 近景`）→ 需要 `clean_time()` 提取纯时间
- ❌ 脚本行有重叠时间段（52-55s 和 53-57s）→ start 时间匹配解决
- ❌ 道具已存在于 scene 描述中 → 注入前检查前3个词是否已有
- ❌ S-XX 映射被动作推断覆盖后，所有 S-XX 行都变新场景 → 仅在推断≠映射时更新

### 场景图 / 道具图 Reference 体系（v2.2 ⭐ 2026-04-29 新增）

> **背景**：视频生成工具（Plank/Seedance 等）支持参考图输入。为保持场景和关键道具的一致性，我们为每个场景和关键道具生成独立的 reference prompt（纯环境/静物图），然后在关键帧 prompt 中用引用标记指向它们，而非重复写完整描述。

**核心优势：**
- 场景只描述一次 → 全剧一致性
- 关键帧 prompt 大幅精简 → 节省 token
- 视频生成时参考图 + 精简 prompt 一起传入 → 效果更好

**数据模型（`project_data.json` 新增顶级字段）：**

```json
{
  "scenes": [
    {
      "id": "S-01",
      "name": "Laura卧室",
      "prompt": "Gothic Korean manga style, 9:16 vertical, wide establishing shot, no characters, environmental scene reference, Gothic Victorian bedroom, cool candlelight tones, heavy velvet curtains, carved Victorian bed with tall posts, ornate antique mirror, bedside candlestick, stone walls, moonlight through arched window",
      "status": "pending"
    }
  ],
  "props": [
    {
      "id": "P-01",
      "name": "日记",
      "prompt": "Gothic Korean manga style, close-up still life, no characters, prop reference, leather-bound diary with aged pages and old handwriting, open on dark wooden desk, candlelit",
      "status": "pending"
    }
  ]
}
```

**关键帧 Prompt 改造：**

```
改前（场景描述嵌在 prompt 里）：
Gothic Korean manga style, 9:16 vertical, close-up,
scene: [Gothic Victorian bedroom, cool candlelight tones, heavy velvet curtains...],
a 17-year-old girl waking in terror...

改后（用引用标记替代场景描述）：
Gothic Korean manga style, 9:16 vertical, close-up,
[ref: S-01],
a 17-year-old girl waking in terror, hand touching her neck, Victoria nightgown
```

**Image Prompt 新增字段：**
```json
{
  "frame": 1,
  "time": "0-2s 特写",
  "scene_ref": "S-01",
  "prop_refs": ["P-01", "P-02"],
  "prompt": "Gothic Korean manga style, 9:16 vertical, close-up, [ref: S-01], a girl..."
}
```

**场景 Reference Prompt 写法规则：**
- 开头：风格 + 画幅 + `wide establishing shot`
- 包含：`no characters, environmental scene reference`（纯环境，不含角色）
- 描述：场景的完整视觉特征（风格、色调、光源、标志性元素）
- 每个唯一场景写一个，全剧约 10-15 个

**道具 Reference Prompt 写法规则：**
- 只覆盖**关键道具**（跨集出现、需要一致性的）
- 开头：风格 + `close-up still life`
- 包含：`no characters, prop reference`（静物特写）
- 描述：形状、材质、颜色、摆放环境
- 典型关键道具：日记、匕首、画像、特效（金色/紫色光/雾）等
- 龙套道具（茶杯、毛毯等）不需要单独写

**执行流程：**
1. 遍历全部分镜 imagePrompts，提取唯一场景（去重后 ~10-15 个）
2. 为每个场景写 prompt（纯环境描述）
3. 从 manifest 道具清单筛选关键道具（出现 ≥2 集）
4. 为每个关键道具写 prompt（静物特写）
5. 改造关键帧 prompt：删除 `scene: [...]` 和重复的道具描述，替换为 `[ref: S-XX]` + `scene_ref` / `prop_refs` 字段
6. 将场景/道具 Reference Prompt 章节**追加到 manifest.md** 末尾
7. 生成 `scene_prop_data.json` 数据结构（scenes 数组 + props 数组）
8. 更新 `project_data.json` 结构
9. 更新 `build_html.py`：新增"场景管理"和"道具管理" Tab 页（见 references/v2.2-migration.md）
10. 重新生成 `index.html`

> **v2.2 执行检查清单 → v2.3 三文件检查清单（每轮必须验证）**：
> 1. `characters.md` 是否完整（角色性格、动机、关系）？
> 2. `scene_prop_data.json` 是否存在且含 scenes/props 数组（每个唯一场景一个 prompt）？
> 3. `manifest.md` 是否精简（只含服装指南、表情库、全局规则，不含角色外观/场景描述重复内容）？
> 4. Prompts 中的场景描述是否已替换为 `[ref: S-XX]` 引用标记？
> 5. 改造后每集的 `[ref: S-XX]` 标记数是否 ≥ 帧数？
> **任一未通过 → 必须先补完再继续分镜/生图。**

**迁移脚本模板见**：`scripts/migrate_v2.2.py`（可复用模板，编辑 SCENES/PROPS/KEYWORDS 后直接运行）

### 角色 Reference 体系（v2.3 ⭐ 2026-04-30 Carmilla 项目验证新增）

> **背景**：同场景/道具，角色外观描述在每个 prompt 中重复，导致 token 浪费 + 跨集角色漂移。将角色外观收敛为 `[ref: C-XX]` 引用，prompt 只保留服装 + 表情叠加。

**核心优势：**
- 角色外观只定义一次 → 全剧一致性
- 每张 frame prompt 省 ~50% token（去掉 80-120 词的角色重复描述）
- 改角色外观只需改一处（`characters.md` 的 `base_prompt`）

**数据模型（`characters.md` 扩展）：**

```markdown
## Carmilla
- **base_prompt**: Gothic Korean manga style, 175cm tall vampire woman, pale skin, shoulder-length black wavy hair, amber eyes, fangs
- **outfits**:
  - **black_dress**: black Victorian gown with silver necklace
  - **white_dress**: white silk evening gown
  - **casual**: dark coat with leather boots
- **expressions**:
  - **fear**: dilated pupils, trembling lips, retreating
  - **seductive**: half-lidded eyes, slight smirk, leaning forward
  - **angry**: narrowed eyes, clenched jaw, glowing amber eyes
```

**Image Prompt 改造（角色部分）：**

```
改前（内嵌完整角色描述）：
Gothic Korean manga style, 9:16 vertical, close-up,
[Carmilla: pale skin, shoulder-length black wavy hair, amber eyes, fangs, black Victorian gown with silver necklace],
scene: [Gothic Victorian bedroom...],
a vampire woman looking in terror...

改后（角色 ref + 服装 + 表情）：
Gothic Korean manga style, 9:16 vertical, close-up,
[ref: C-01], black_dress, fear,
[ref: S-01],
a vampire woman looking in terror...
```

**Image Prompt 新增字段：**

```json
{
  "frame": 1,
  "time": "0-2s 特写",
  "char_refs": ["C-01"],
  "char_outfits": ["C-01:black_dress"],
  "char_expressions": ["C-01:fear"],
  "scene_ref": "S-01",
  "prop_refs": ["P-01"],
  "prompt": "Gothic Korean manga style, 9:16 vertical, close-up, [ref: C-01], black_dress, fear, [ref: S-01], ..."
}
```

**角色 Reference Prompt 写法规则：**
- `base_prompt`：风格 + 体型 + 肤色 + 发型发色 + 瞳色 + 标志性特征（尖牙、疤痕等）
- `outfits`：按剧情阶段命名（如 `prison_uniform`、`evening_gown`），不含角色基本信息
- `expressions`：情绪关键词组合（瞳孔 + 嘴唇 + 姿态）

**执行流程：**
1. 为每个角色写 `base_prompt`（从现有 characters.md 外观描述精简）
2. 梳理全剧服装，按角色归纳为 `outfits` 字典
3. 梳理表情关键词为 `expressions` 字典
4. 批量改造 prompts：`完整角色描述` → `[ref: C-XX], outfit_key, expression_key`
5. 多角色同框：每个角色都用 `[ref: C-XX]` 格式
6. 更新 `build_html.py` 角色 Tab：显示 reference 视图 + 一键复制

> **完整 v2.3 检查清单（扩展）**：
> 6. Prompts 中的角色描述是否已替换为 `[ref: C-XX]` 引用标记？
> 7. 改造后每集的 `[ref: C-XX]` 标记数是否 ≥ 出场角色数 × 帧数？
> 8. `characters.md` 是否含 `base_prompt` / `outfits` / `expressions` 三个字段？

> 💡 **从 Hollywood Screenplay 入手的快速路径**（2026-04-30 Count of Monte Cristo 项目验证）：
> 当用户直接提供好莱坞格式剧本（非小说），跳过阶段1-2，直接：
> 1. 解析 screenplay → 提取 EP 分集 + 场景头(INT./EXT.) + 对白 + Voiceover
> 2. 并行生成：人物设定 + 视觉资产清单（用 delegate_task 各派一个Agent）
> 3. 写分镜（EP1-5 Demo 先做）
> 4. 写 Prompts（必须包含 v2.2 Reference 体系！）
> 5. 补 scene_prop_data.json + manifest.md Reference 章节
> 6. 改造 Prompts 用 `[ref: S-XX]`
> **完整执行顺序**：人物 → 视觉资产 → 分镜 → Prompts → **Reference 体系**（场景图+道具图+引用标记）

> 💡 **导演修订剧本的更新路径**（2026-04-30 Carmilla 项目验证）：
> 当用户发送导演优化后的新剧本，更新已有项目：
> 1. 读取新剧本（PDF → pymupdf 提取文本 → 保存 .txt，或 DOCX → python-docx 解析）
> 2. 按 `EPISODE \d+:` 切分 → 提取每集标题/场景/对白
> 3. **对比新旧**：集名变化？对白变化？新增角色？集数增减？
> 4. 更新 INDEX.md（集名映射）
> 5. 批量更新 script/EP-XX.md
> 6. 更新 characters.md（如有新角色）
> 7. 更新 MASTER.md（如三幕结构变化）
> 8. 更新 generate_index.py（episode range + 解析器兼容新格式）
> 9. 运行 generate_index.py + build_html.py 重新生成工作台
> **⚠️ 先做 Demo（1-2集）确认风格再批量处理全部**
>
> 💡 **剧本修订闭环流程**（v2.7+）：当收到编剧修订版时：
> 1. **版本对比**：按集切分两版，对比标题/字符数/行数/对白数
> 2. **质量审计**（5项必查）：角色名错误、过度删减(Δ>-20%)、结尾缺失(FADE OUT)、Epilogue独立、修订说明残留
> 3. **学习编剧修改逻辑**：句式简化方向(长→短)、对话风格一致性(古典vs口语)、格式标准化(CONT'D/FADE OUT)、节奏感知(从删减幅度反向推导)
> 4. **更新Prompt**：将学到的风格规则写入 TASK.md 的 Style Guide 章节
> 5. **提意见**：发现不理想修改要指出（关键情感过度简化、高潮戏压缩、角色独特性丢失）
>
> ⚠️ **v3.1 关键教训（Carmilla v1→v2 踩坑）**：
> - **永远确认"分镜基于哪个剧本版本"** — v1 和 v2 可能完全不同（Carmilla v1 改了 1207 行，v2 只改了 37 行）。分镜如果基于 v1 生成，v2 来了要全部重来。
> - **新版本剧本 → 用 `difflib.SequenceMatcher` 自动量化差异量**：
>   ```python
>   import re, difflib
>   # 新脚本按集拆分
>   ep_pattern = re.compile(r'^EPISODE (\d+):', re.MULTILINE)
>   ep_splits = list(ep_pattern.finditer(new_script))
>   for i, m in enumerate(ep_splits):
>       ep_num = int(m.group(1))
>       new_text = new_script[m.start():ep_splits[i+1].start() if i+1 < len(ep_splits) else len(new_script)]
>       old_text = open(f'script/EP-{ep_num:02d}.md').read()
>       ratio = difflib.SequenceMatcher(None, new_text, old_text).ratio()
>       if ratio < 0.7: print(f"EP-{ep_num:02d}: {ratio:.0%} → 需全量重写")
>       elif ratio < 0.95: print(f"EP-{ep_num:02d}: {ratio:.0%} → 增量修改")
>       else: print(f"EP-{ep_num:02d}: {ratio:.0%} → 无需修改")
>   ```
>   **经验值**：ratio < 70% → 全量重写分镜+Prompts；70-95% → 增量修改；>95% → 无需改动
> - **保留原始剧本**：`carmilla_full_text.txt`（原始）、`carmilla_modified.txt`（v1）、`carmilla_revised_v2.txt`（v2）都要保留，版本清晰。
> - **Index 页面数据源跟着剧本版本走**：剧本换了，project_data.json 要重新生成，index.html 要重新 build。
> - **影响范围判定**：剧本全换 → 分镜全换 → Prompts 全换；角色人设/Manifest/已生成图片可保留。

## 审核员系统（三视角定性 + 三Aligner定量）

> v3.0 核心变化：三视角定性评审团 + 三专用 Aligner 定量评分，合二为一。
> - 三视角评审团 → 定性（哪里不好 + 为什么）
> - 三专用 Aligner → 定量（具体扣多少分，≥80 PASS / 70-79 ⚠️ / ≤70 FAIL）

## 整体架构

```
输入内容 → 路由（判断类型） → 选择对应 Aligner
                                     │
                          三视角评审团（定性）
                          ┌──────────┼──────────┐
                          急躁哥    逻辑控     视听专家
                                     │
                          Script / Storyboard / Prompt-Aligner（定量）
                                     │
                          综合报告 → 🔴🟡🟢 分级优化清单
```

## 路由逻辑

根据输入内容自动选择审核模式：

| 输入特征 | 路由到 | 示例 |
|---------|--------|------|
| `## Scene` / `## Dialogue` / 剧本格式 | Script-Aligner | `script/EP-XX.md` |
| `\| # \| Time \| Shot \| Camera \|` / 分镜表格 | Storyboard-Aligner | `storyboard/EP-XX.md` |
| 角色外观描述 / `--image` / 参考图 / 风格关键词 | Prompt-Aligner | `prompts/EP-XX.md` |
| 标题/大纲/人设/视频成片 | 三视角定性 + 对应 Aligner | 用户发全剧 |
| 无法判断 | 先用三视角定性，再问用户 | 自由格式 |

---

## 一、三视角评审团（定性层）

> 评审团提供"哪里不好 + 为什么"，Aligner 提供"具体扣了多少分"。

### 角色定义

| 视角 | 关注点 | 容忍度 |
|------|--------|--------|
| **急躁哥** (Impatient Bro) | 节奏、爽点、反转 | 极低（没冲突就划走） |
| **逻辑控** (Logic Master) | 逻辑、类型定位、差异化、世界观一致性 | 低（逻辑硬伤不可接受） |
| **视听专家** (Visual Expert) | AI制作可行性、视觉一致性、成本预估 | 中（关注技术实现） |

### 国际化人设切换

**评审前必做：确认目标市场 → 切换人设。**

| 角色 | 欧美市场 | 日韩市场 | 国内市场 | 东南亚市场 |
|------|---------|---------|---------|-----------|
| 急躁哥 | 30 岁拉丁裔女，保姆/服务员，ReelShort 重度用户 | 26 岁 OL，Line TV/DramaBox 用户 | 28 岁外卖骑手，抖音快手 | 26 岁工厂女工，TikTok 短剧 |
| 逻辑控 | 32 岁 SF/NY Tech PM | 30 岁内容编辑 | 32 岁互联网 PM | 29 岁数字营销 |
| 视听专家 | 45 岁 ReelShort 制片人 | 40 岁日/韩 PD | 45 岁资深制片人 | 38 岁区域发行 |

### Industry Ground Truth (基于真实数据)

这些洞察来自 2025-2026 年海外短剧行业数据：

**什么有效 ✅**
| 洞察 | 来源 |
|------|------|
| 越简单直接越受欢迎 — 玛丽苏 > 复杂剧情 | 之桃影视制片人朱古力 |
| 声音是付费驱动因素 — 气泡音/骚讲话 | 朱古力实地观察 |
| 女频全球通吃 — 核心受众是拉丁裔/东南亚社会下层女性 | 36氪 2025Q1 |
| 黑帮 + 狼人题材火爆 — "强制爱 + 身份觉醒"组合 | 2025年2月市场数据 |
| 情感陪伴 > 剧情深度 — 观众要的是情绪价值，不是逻辑 | 之桃影视 2024 复盘 |

**什么踩坑 ❌**
| 踩坑 | 原因 |
|------|------|
| 悬疑/强剧情路线行不通 | 观众"不花钱也能忍" |
| 精致但不爽 — 百万美金制作但数据不好 | 竖屏限制 + 观众耐心有限 |
| 闪婚失忆认不出老公 | 海外结婚证没有照片 |
| 自助洗衣房场景 | 海外不常见 |
| 过度"虐女"情节 | 海外女性观众反感 |

### 节奏公式（行业验证）

```
慢推蓄力 → 静默 → 爆发 → 快切 → 钩子
```

### 评审框架（三视角定性）

#### 评审剧本

| 维度 | 急躁哥 | 逻辑控 | 视听专家 |
|------|--------|--------|----------|
| 核心问题 | 有没有爽点和情绪陪伴 | 节奏卡点是否准确、动机是否合理 | 场景成本、技术可行性 |
| 关键指标 | 3 秒钩子、10 秒爽点、结尾钩子 | 每 30 秒新信息、人设一致性 | 每集 1-3 分钟、竖屏适配 |
| 差评信号 | 平铺没有冲突、结尾无悬念 | 角色行为无动机、信息缺失 | 场景过多、转场不自然 |

#### 评审分镜

| 维度 | 急躁哥 | 逻辑控 | 视听专家 |
|------|--------|--------|----------|
| 核心问题 | 画面是否有冲击力 | 分镜逻辑是否连贯 | 运镜是否可执行、Seedance 限制 |
| 关键指标 | 每个镜头有情绪信号 | 场景切换有理由 | 每镜头 1 种运镜、慢动作优先 |
| 差评信号 | 空镜头、无表情、画面呆板 | 时序混乱、场景跳跃 | 运镜过多、双人互动（易翻车） |

#### 评审集间衔接

| 维度 | 急躁哥 | 逻辑控 | 视听专家 |
|------|--------|--------|----------|
| 核心问题 | 上集的钩子有没有在下集被接住 | 角色状态是否一致 | 过渡镜头是否自然 |
| 关键指标 | 下集前 5 秒回收上集情绪 | 角色动机连贯、线索延续 | 闪回/闪前技术可行性 |
| 差评信号 | 上集结尾情绪被丢弃 | 角色行为前后矛盾 | 场景位置不合理无过渡 |

---

## 二、三专用 Aligner（定量层）

每个 Aligner 独立 100 分制，≥80 PASS / 70-79 ⚠️ / ≤70 FAIL。

### A. Script-Aligner（审剧本）— 100 分

**前置：确认目标市场，整个审核的"尺子"跟着调。**

#### 区域适配矩阵

| 区域 | 钩子标准 | 情绪表达偏好 | 节奏容忍 | 文化雷区 |
|------|---------|-------------|---------|---------|
| **欧美** | 2秒进冲突 | 爆炸式（"I want you to suffer!"） | 极低（5秒没爽点走人） | GL避免"未成年+永久身体改变"；宗教隐喻过重 |
| **日韩** | 5秒氛围铺垫可接受 | 克制+内心戏 | 中等（能接受10秒情绪积累） | 等级/权力关系敏感；过度暴力需缓冲 |
| **国内** | 2秒打脸 | 直白+反转 | 低（3秒没冲突划走） | 审核红线；价值观导向 |
| **东南亚** | 3秒情感+冲突 | 含蓄但有爆发点 | 低 | 宗教敏感（伊斯兰/佛教）；家族伦理 |

#### 评分表

| # | 检查项 | 满分 | 判定要点 |
|---|--------|------|---------|
| 1 | **开局钩子** | 15 | 前 N 秒必须有视觉冲击/冲突（N 按区域适配：欧美2s、日韩5s、国内2s、东南亚3s） |
| 2 | **冲突强度** | 20 | 每集冲突绑定不可逆代价，非"口头争吵就完事" |
| 3 | **悬念钩子** | 15 | 根据本集内容类型动态选择最匹配的钩子（见下方10级参考），非模糊暗示。钩子类型需标注 |
| 4 | **人物弧光** | 10 | 主角有成长线，反派有悲剧内核 |
| 5 | **核心关系** | 10 | 体现核心关系卖点（每集必须有） |
| 6 | **世界观逻辑** | 10 | 规则一致性、无临时加设定、角色知识合理、视觉变化有解释 |
| 7 | **节奏/平台** | 10 | V.O.≤2句、≥60%段落含动作、连续3集不重复同一冲突类型 |
| 8 | **文化敏感** | 5 | 年龄+行为组合、宗教/政治隐喻、原谅需有前置铺垫 |
| 9 | **信息密度** | 5 | 每集≥2个新信息点 |
| | **合计** | **100** | |

#### 扣分示例

```
- 钩子类型与本集内容不匹配 → -10分（如高潮集用了信息钩子但本集是生死对决）
- 悬念钩子无类型标注 → -3分
- 前 N 秒无视觉事件（按区域标准）→ -10分
- 冲突无不可逆代价 → -15分
- 结尾悬念模糊 → -10分
- 角色动机断裂（施暴者→忏悔者无过渡）→ -5分
- 高潮处临时加设定 → -5分
- 连续 3 集同冲突类型 → -8分
- V.O. 设定解说 > 2 句 → -3分
- 发现平台敏感组合未缓冲 → -3分
```

#### 🔥 叙事钩子等级表（v3.5 ⭐ 新增）

> 源自叙事钩子 10 级体系。编剧写 Cliffhanger 时标注类型，Aligner 审核时检查强度是否匹配当前集阶段。

| 等级 | 类型 | 核心原理 | 短剧示例 |
|------|------|---------|---------|
| 1 | **信息钩子** | 信息缺口 → 人脑想补全 | "名册最后一页写着..." |
| 2 | **异常钩子** | 反常事 → 人心好奇 | "吸血鬼居然流了眼泪" |
| 3 | **危险钩子** | 威胁 → 生存本能 | "Carmilla 獠牙逼近颈动脉" |
| 4 | **欲望钩子** | 观众想看角色得到/失去什么 | "他终于说出了那三个字" |
| 5 | **关系钩子** | 核心关系面临转折/破裂 | "两个敌人发现彼此是同父异母" |
| 6 | **羞耻钩子** | 角色被暴露、被看穿、被羞辱 | "所有人都知道了她的秘密" |
| 7 | **不可逆钩子** | 发生了回不去的事 | "父亲撕毁了名册关键页" |
| 8 | **误判钩子** | 观众/角色以为 A，其实是 B | "以为是救赎，其实是陷阱" |
| 9 | **后果链钩子** | 一个后果引发连锁反应 | "Laura 变身→被父亲发现→赶出家门→流落街头" |
| 10 | **复合钩子** | 同时触发 2-3 种钩子类型 | 身份暴露(羞耻6)+撕毁名册(不可逆7)+父亲破门(危险3)+瞳孔变色(异常2) |

**钩子选择原则（动态，不套用公式）**：

先判断本集内容类型（囚禁集/对峙集/闪回集/揭示集/高潮集/日常铺垫...），再选最匹配的钩子类型：

| 集类型 | 推荐钩子方向 | 示例 |
|--------|------------|------|
| **揭示集**（身份/真相揭晓） | 异常(2) + 误判(8) | "以为是人，其实是吸血鬼" |
| **对峙集**（正面对决） | 危险(3) + 不可逆(7) | "刀架在颈上，决定无法收回" |
| **关系转折集**（情感/信任变化） | 关系(5) + 羞耻(6) | "他看到了不该看的" |
| **日常铺垫集** | 信息(1) + 欲望(4) | "日记最后一页缺了一角" |
| **高潮/结局集** | 后果链(9) → 复合(10) | 多个线索同时收束 |

**审核判定（动态评估）**：
- ✅ 钩子类型匹配本集内容，且让观众有"不看不行"的冲动 → 满分
- ⚠️ 钩子可用但强度偏弱（如高潮集只用了信息钩子）→ 扣 5 分
- ❌ 钩子与本集内容脱节（如日常集用了后果链却无前置铺垫）→ 扣 10 分
- ❌ 无类型标注 → 扣 3 分（编剧需写 `Hook: [类型名称+等级]`）

**核心原则**：10 级是**词汇表**不是公式。编剧根据本集实际情节选最适配的钩子，Aligner 审核时判断"这个钩子是否有效服务了这集的内容"，而不是"这集必须 N 级"。后期集倾向于高级钩子（情绪驱动）是因为付费转化需要，但如果本集就是铺垫性质，低等级钩子也能 PASS。

#### 输出格式

```
## EP-XX Script 审核报告

| 维度 | 满分 | 得分 | 判定 | 扣分理由 |
|------|------|------|------|---------|
| 开局钩子 | 15 | XX | ✅/❌ | ... |
| 冲突强度 | 20 | XX | ✅/❌ | ... |
| ... | ... | ... | ... | ... |
**总分: XX/100** → PASS ✅ / ⚠️ / FAIL ❌
**修改建议:** 1. ... 2. ... 3. ...
```

---

### B. Storyboard-Aligner（审分镜）— 100 分

**核心原则：不看公式，看"这集的内容是否被分镜有效服务了"。**
先判断集类型（囚禁/对峙/闪回/高潮/氛围...），再评估分镜是否匹配。

#### 评分表

| # | 维度 | 满分 | 检查方式 |
|---|------|------|---------|
| 1 | **节奏分层** | 20 | ⚡ **动态评估**：这集的爆发点/情绪点/过渡镜头，时长是否形成张弛对比？不是"所有惊悚都要0.5s"，而是"这个场景的关键时刻有没有被时长区分出来"。检查：① 是否有时长突变点（每3-4镜一个节奏锚点）② 信息是否过载（1秒内塞2种情绪→需拆分）③ 情绪镜头是否给足反应时间 |
| 2 | **运镜匹配度** | 20 | 🎯 **动态评估**：每个场景的运镜是否服务于该场景的情绪/氛围？检查：① 恐怖场景有无不稳定感（POV/手持/畸变）② 亲密场景有无压迫感（微距/慢推/画外空间）③ 冲击场景有无动态运镜（摇晃/快拉）④ 揭示场景有无焦点变化 |
| 3 | **景别层次** | 15 | 📐 **动态评估**：这集核心信息是什么？景别是否有效传达？检查：① 囚禁集偏特写合理，但有无层次变化（至少1个全景+1个极端特写）② 对峙集有无"中景建关系→特写抓表情→极端特写抓关键"的递进 ③ 是否景别单一导致视觉疲劳 |
| 4 | **时空切换** | 15 | 🔗 闪回/场景切换是否有衔接三件套：① 动作承接（角色物理反应）② 视觉锚点（MATCH CUT 同一道具）③ 音效联动。情感转折是否有前置铺垫镜头（1秒微表情/动作） |
| 5 | **AI指令颗粒度** | 15 | 🤖 每个镜头是否有 AI 可执行的指令：① 特效参数明确（位置/颜色/透明度）② AI约束词（面部不扭曲/液体不穿模/肢体不穿插）③ 光影描述具体 |
| 6 | **情绪递进** | 15 | 🌊 **动态评估**：这集情绪终点是什么？镜头是否支撑弧线？不强制"平静→爆发→回落"，而是检查：① 情绪变化是否被镜头语言"看见" ② 角色弧光转折是否有运镜/光影对比（如恐惧=特写+摇晃 vs 决心=中景+稳定） |
| | **合计** | **100** | |

#### 🔥 Atmosphere 列常见错误（v3.3 ⭐ 2026-05-15 导演纠正）

- ❌ **写成情绪词**：如"恐怖压抑"、"暧昧紧张"、"悲伤回忆" — 这些属于 Description 列
- ✅ **写成物理环境**：如"深夜/雨/闪电"、"黄昏/阴/微光"、"室内/无窗/人工光"
- **根因**：Atmosphere 是 Lighting 列的前置条件。先知道"深夜+雨+闪电"，Lighting 才能据此推理光源（闪电冷白+烛火暖黄+暗角）。如果写了"恐怖压抑"，Lighting 无法从中推导出实际光源。
- **检查项**：Atmosphere 列中的词是否能在实际场景中"看到"（天气/时间/光线）而非"感觉到"（情绪）

#### 集类型参考（非强制规则，仅帮助判断）

| 集类型 | 典型镜头数 | 节奏特点 | 景别倾向 |
|--------|-----------|---------|---------|
| 氛围 | 16-18 | 慢节奏，长镜头多 | 全景/中景为主 |
| 标准 | 18-22 | 节奏均衡 | 五景混合 |
| 恐怖 | 20-24 | 快慢交替，张弛感强 | 特写+极端特写多 |
| 高潮 | 22-25 | 快节奏+关键时刻拉长 | 全范围 |
| 囚禁 | 18-22 | 压迫感节奏 | 特写/近景为主，需层次 |

#### 输出格式

```
## EP-XX 分镜审核报告

集类型判断：[囚禁/对峙/闪回/高潮/氛围/...]

| 维度 | 满分 | 得分 | 判定 | 分析与建议 |
|------|------|------|------|-----------|
| 节奏分层 | 20 | XX | ✅/❌ | 本集是XX类型，时长分布... |
| 运镜匹配度 | 20 | XX | ✅/❌ | 恐怖场景用了XX运镜... |
| 景别层次 | 15 | XX | ✅/❌ | 核心信息是XX，景别... |
| 时空切换 | 15 | XX | ✅/❌ | 闪回衔接... |
| AI指令颗粒度 | 15 | XX | ✅/❌ | 特效参数... |
| 情绪递进 | 15 | XX | ✅/❌ | 情绪终点是XX，镜头... |
**总分: XX/100** → PASS ✅ / ⚠️ / FAIL ❌
**修改建议:** 1. ... 2. ... 3. ...
```

---

### C. Prompt-Aligner（审 AI Prompts）— 100 分

**职责：确保 Prompt 文件能生成高质量、一致性的 AI 画面。**

#### 评分表

| # | 维度 | 满分 | 检查项 |
|---|------|------|--------|
| 1 | **角色外观一致性** | 25 | 每角色的瞳色/发色/服装/疤痕/年龄特征与 manifest.md 精确匹配；多角色同框每个都有完整外观描述 |
| 2 | **场景还原度** | 15 | 场景描述与 manifest.md 视觉设定一致；9:16 竖屏参数；场景氛围描述具体（非"神秘氛围"等模糊词） |
| 3 | **特效指令明确性** | 15 | 特效有精确参数：位置（"右上角"/"颈部"）、颜色（"深紫带微光"）、透明度（"半透明"）、不遮挡规则 |
| 4 | **AI 瑕疵规避** | 15 | 是否包含约束词：面部不扭曲、液体不穿模、肢体不穿插、动作连贯不卡顿 |
| 5 | **参考图利用** | 15 | 正确使用 reference images（--image 权重渐变、关键帧法）；双人场景是否拆分避免 AI 翻车 |
| 6 | **Prompt 可执行性** | 15 | 描述具体可执行；语言/格式统一（全英文或全中文）；风格关键词一致（如哥特暗黑） |
| | **合计** | **100** | |

#### 扣分示例

```
- 角色外观与 manifest 不一致（瞳色/发色/服装）→ -5分
- 多角色同框缺角色外观描述 → -3分/个
- 特效指令模糊（如只写"发光"无颜色/位置）→ -3分
- 缺少 AI 约束词（面部/液体/肢体）→ -3分
- 双人亲密场景未拆分 → -3分
- Prompt 使用模糊词（"神秘"、"氛围感"）→ -2分
- 风格关键词前后不一致 → -2分
```

#### 输出格式

```
## EP-XX Prompt 审核报告

| 维度 | 满分 | 得分 | 判定 | 问题 |
|------|------|------|------|------|
| 角色外观一致性 | 25 | XX | ✅/❌ | Carmilla 瞳色应为琥珀色，但#3写金色 |
| 场景还原度 | 15 | XX | ✅/❌ | ... |
| 特效指令明确性 | 15 | XX | ✅/❌ | ... |
| AI 瑕疵规避 | 15 | XX | ✅/❌ | ... |
| 参考图利用 | 15 | XX | ✅/❌ | ... |
| Prompt 可执行性 | 15 | XX | ✅/❌ | ... |
**总分: XX/100** → PASS ✅ / ⚠️ / FAIL ❌
**修改建议:** 1. ... 2. ... 3. ...
```

---

## 三、综合工作流

### 单集审核流程

```
1. 用户发送内容 → 路由判断类型
2. 三视角评审团定性分析（急躁哥/逻辑控/视听专家）
3. 对应 Aligner 定量评分（Script/Storyboard/Prompt）
4. 交叉验证：定性问题 + 定量扣分 → 确认严重程度
5. 输出综合报告（定性吐槽 + 定量评分 + 🔴🟡🟢 优化清单）
```

### 全剧审核流程

```
1. 用户发送全剧三件套
2. 逐集跑对应 Aligner（可并行读文件，串行出报告）
3. 汇总全剧评分 → 通过/未通过集数统计
4. 集间衔接检查（Cross-Episode Continuity）
5. 输出全剧综合报告
```

### 审核→修改闭环

```
1. 🔴 必须修改 → 直接修改对应文件（write_file 全量重写）
2. 🟡 建议优化 → 修改或制作阶段处理
3. 🟢 锦上添花 → 制作阶段处理
4. 修改后重新跑对应 Aligner → 直到 ≥ 80 分
```

---

## 四、集间衔接检查（Cross-Episode Continuity）

| # | 检查项 | 典型断裂 |
|---|--------|---------|
| 1 | 开场回收上集结尾钩子 | 下集跳新场景，上集核心情绪被丢弃 |
| 2 | 角色动机连贯 | 上集"放下仇恨"，下集又冷酷复仇 |
| 3 | 悬念线索延续 | 上集铺垫的秘密，下集不再提起 |
| 4 | 角色状态一致 | 受伤角色下一集消失；觉醒能力重复"发现" |
| 5 | 场景位置合理 | 上集在 A 地，下集在 B 地，无过渡 |

**修复手法：**
- 下集前 5 秒必须接上集结尾
- 角色转变需要独白或台词解释"为什么"
- 闪回收拢形成情感闭环

---

## 五、大项目处理策略

> **15 集以上项目，不要用子代理做审核。**

- 子代理 context 有限，读完 10 集就 max_iterations 超时
- **正确做法**：主模型直接处理
  1. 用 read_file 快速读关键集（前 5 集 + 高潮 + 结局）
  2. 主模型直接输出审核报告

---

## 六、常见陷阱

| # | 陷阱 | 解决 |
|---|------|------|
| 1 | 跨集衔接断裂 | 每集写完检查下集开场是否回收 |
| 2 | 只用单一视角评审 | 三视角 + 对应 Aligner |
| 3 | 标准过于模糊 | 量化评分 + 具体扣分理由 |
| 4 | 缺乏优先级 | 🔴🟡🟢 分级处理 |
| 5 | 套用公式审分镜 | 先判断集类型，再动态评估 |
| 6 | 对英文剧名用国内人设 | 先确认市场，再切换人设 |
| 7 | 审核员 context 包含编剧意图 | 只看成品，不包含意图说明 |
| 8 | 悬疑强剧情路线 | 海外观众"不花钱也能忍" |
| 9 | 忽略声音 | 声音是海外用户付费的核心驱动因素 |
| 10 | 忽略文化差异 | 闪婚失忆（结婚证无照片）、撒红酒 vs 泼咖啡 |

---

## Output Format（综合报告）

```markdown
# 【短剧评审团综合报告】

## 评审信息
- 目标市场：[欧美/日韩/国内/东南亚]
- 评审类型：[标题/剧本/分镜/集间衔接/人设/视频]
- 评审内容：[内容摘要]

## 定性评审（三视角）

### 【急躁哥吐槽】
[口语化，秒级反应，关注爽点和情绪]

### 【逻辑控分析】
[数据驱动，关注类型定位、信息密度、差异化]

### 【视听专家诊断】
[专业视角，关注商业数据、竞品对标、踩坑预警]

## 定量评审（Aligner）

[对应 Script / Storyboard / Prompt-Aligner 评分表]

**总分: XX/100** → PASS ✅ / ⚠️ / FAIL ❌

## 优先级优化建议

### 🔴 必须修改（影响留存/付费转化）
1. [具体问题] → [具体方案]

### 🟡 建议优化（提升体验）
1. [具体问题] → [具体方案]

### 🟢 锦上添花（专业升级）
1. [具体问题] → [具体方案]
```

---

## Examples

### Example: Reviewing a Title (US Market)

**Input:** Title "My CEO Loves My Voice"

**Output:**
```markdown
# 【短剧评审团综合报告】

## 评审信息
- 目标市场：欧美
- 评审类型：标题
- 评审内容：My CEO Loves My Voice

## 定性评审

### 【急躁哥吐槽】
💬 "CEO loves my voice? Not my face, not my body? WHAT?"
🔥 冲动程度：立刻点击

### 【逻辑控分析】
🎯 类型锚点：明确 — romance + 声音设定
📊 信息密度：高 — 7 个词，每个都有作用

### 【视听专家诊断】
💰 商业潜力：高 — 行业数据验证"声音"是付费驱动因素

## 优先级优化建议

🟢 锦上添花：海报设计加入声音波形/耳机等视觉元素
```

### Example: Reviewing a Title (US Market)

**Input:** Title "After Hours"

**Output:**
```markdown
## 定性评审

### 【急躁哥吐槽】
⭐⭐ "下班后？什么剧？不知道点不点"

### 【逻辑控分析】
⭐⭐ 信息量趋近于零，SEO 为零

### 【视听专家诊断】
⭐⭐⭐ 品牌感强但没有类型提示，会被淹没

## 优先级优化建议

🔴 必须修改：加副标题或 genre 标签（如 *After Hours: His Secret Line*）
```

---

## Reviewer-Combo 与 Aligner 的关系

```
本技能审核系统 = 三视角定性（急躁哥/逻辑控/视听专家） + 三Aligner定量（Script/Storyboard/Prompt）

使用场景：
1. 标题/大纲评审 → 三视角定性即可
2. 剧本评审 → 三视角定性 + Script-Aligner定量
3. 分镜评审 → 三视角定性 + Storyboard-Aligner定量
4. Prompts评审 → 三视角定性 + Prompt-Aligner定量
5. 全剧评审 → 三视角定性 + 对应Aligner定量 + 集间衔接检查
```

## 相关技能

- `hermes-short-drama-team` — 短剧编剧全流程系统
- `short-drama-production-index` — 短剧工作台 JSON/HTML 生成

---

## 短剧创作法则

- 每集必有冲突
- 节奏紧凑密集（3秒没冲突就划走）
- 爽点分布合理
- 人物动机清晰
- 伏笔埋设与回收完整
- **钩子匹配（v3.5 ⭐）** — 结尾 Cliffhanger 根据本集内容类型动态选择最适配的钩子（参考10级体系），不是按集数硬套等级。每集标注 `Hook: [类型+等级]`
- **短句驱动（v2.7 ⭐）** — 每个动作描述 ≤ 2 个分句，用独立短句替代复杂从句（*"her eyes soften"* > *"her eyes full of tenderness—nothing like the creature of the night"*）
- **情感锚点例外（v2.7 ⭐）** — 关键转折点（坦白、最终选择、生死瞬间）保留 1-2 句长描写作情感厚度
- **格式标准（v2.7 ⭐）** — 连续对话必须用 (CONT'D)，集末 FADE TO BLACK/OUT，全剧 FADE OUT + THE END
- **对话风格一致性（v2.7 ⭐）** — 根据项目风格（哥特古典/现代口语）设定，不混用

## 审核通过关键要素（经验总结）

### 1. Face-slap 必须直接暴力
- ✅ **有效**: 泼红酒、推搡、抢物品、肢体冲突
- ❌ **无效**: 口头嘲讽、眼神不屑、翻白眼

### 2. 情感表达必须爆炸式
- ✅ **有效**: "我要你生不如死！"、"你是我的！"、"我找了你三年！"
- ❌ **无效**: "对不起"、"谢谢你"、"是你..."

### 3. Cliffhanger 必须明确
- ✅ **有效**: "Montana 见，我的真爱在那里等你"（发件人：Trent）
- ❌ **无效**: "她不知道，这次旅行将改变她的一生..."

### 4. 危机 - 救援结构
- ✅ **有效**: 巨熊拍向旋翼 → 变身救场 → 认出女主
- ❌ **无效**: 巨熊出现 → 消失 → 男人出现（缺乏戏剧张力）

### 5. 典型迭代次数
- **EP-01**: 通常 3 次（需要建立冲突模式）
- **EP-02**: 通常 4 次（需要建立人物关系）
- **EP-03 后**: 通常 2-3 次（模式已建立）

### 6. 三件套工作流实战教训（2026-04-29 Carmilla项目验证）

**三件套 = 剧本(script/) + 分镜(storyboard/) + AI Prompts(prompts/)**

**第一稿高频翻车点（EP-02首次68分、EP-06首次70分）：**
| 翻车点 | 表现 | 修复后效果 |
|--------|------|-----------|
| 核心关系缺席 | Carmilla零出场/零台词/零情绪关联 | 加入闪回+矛盾心理台词（EP-06: 70→98） |
| 开局依赖上集回收 | 前3秒只是"上集紫纹门缝闪过" | 改为主动视觉冲击（EP-07 v2: 琥珀瞳孔发光开场） |
| 冲突无不可逆代价 | Carmilla闪避、紫纹自然扩散 | 父亲撕毁名册关键页（永久性信息丢失） |
| 无具体倒计时 | 只有"情况在恶化" | 明确"7天倒计时"+"3天内来人" |
| 对白过多 | 19句/集（EP-02 v1） | 压缩到12-15句，每句都有信息量 |
| 正面镜头超标 | 50%+（EP-02 v1） | 用仰拍/俯拍/过肩替代，控制在≤35% |
| 角色外观漂移 | Carmilla瞳色在不同集之间变化 | **v2.0: 用 manifest.md 强制锁定** |

**分镜硬规则（写前检查，避免返工）：**
- 镜头数按集类型：氛围16-18 / 标准18-22 / 恐怖20-24 / 高潮22-25
- 单镜≤5秒（悬念慢推结尾最长10秒）
- 正面镜头≤35% — 优先用仰拍/俯拍/过肩/跟拍
- 运镜种类≥5种 — 最少覆盖：推/侧面/正面+3种其他
- 对白12-15句/集

**审核员Prompt关键设计：**
- 审核员context中**不要包含**编剧的意图说明——只看成品
- 如果上轮审核FAIL，第二轮必须在context中标注上轮扣分项
- 审核员输出"修改建议"时，编剧不要逐条执行——挑核心硬伤修改

**效率提升技巧：**
- 写分镜前先在脚本中标注每个time slot的scene和action
- Prompts文件不需要等审核通过再写——可以三件套一次性写完，然后统一审
- 审核FAIL时重写：保留通过审核的部分，只修改扣分项对应段落

---

## 剧本模板

```markdown
# EP-XX: 标题 | Title
**Duration:** 70s | **Review:** ⭐⭐⭐⭐ PASS (第N轮)

## Aligner Review
- ⚡ 3秒冲突: ✅ 开场直接有冲突/张力
- 💥 直接情感: ✅ 对话爆炸式表达
- 🔥 冲突点: ✅ 核心矛盾明确
- 🎬 悬念: ✅ 结尾有 cliffhanger
- 💬 对话≤15字: ✅ 全部≤15字（弹性）
- 👁️ 视觉一致性: ✅ 角色外观与清单匹配
- ⭐ 评分: XX/100 → PASS ✅

## Scene Breakdown
| Time | Scene | Action | Dialogue (EN/CN) | BGM |
|------|-------|--------|-------------------|-----|
| 0-6s | S-XX 场景 | 动作描述 | "台词" / "中文台词" | 音乐描述 |
| ... | ... | ... | ... | ... |

## Key Dialogue
| EN | CN |
|----|----|
| "英文台词" | "中文台词" |

## Cliffhanger
- **Hook**: [类型名称 + 等级，如"不可逆钩子(7)"或"复合钩子(10): 羞耻(6)+危险(3)"]
- **描述**: [具体悬念内容]
- **下集承接**: [下集开篇3秒必须回收的动作/情绪]
```

## 分镜模板 (v3.1 ⭐ 2026-05-15 导演反馈升级)

> **核心升级**：新增 Scene、Atmosphere、SFX、BGM 四列，Lighting 列升级为三层环境光写法。所有列内容必须根据实际剧本动态推理生成，不写死模板值。

```markdown
# EP-XX: Title - Storyboard

## Episode Info
- **总场景数**: [N] 个 (S-XX 场景A, S-XX 场景B, ...)
- **集时间/天气**: [本集主要时间段+天气，如"夜晚/阴天"或"黄昏/雨"]
- **BGM主线**: [如"低沉弦乐pad → 悲伤大提琴 → 紧张弦乐爆发"]
- **转场音效**: [如"MATCH CUT使用烛光声桥接"或"硬切无声"]

## Key Frames ([N] shots) | Duration: 70s | Type: [atmosphere/standard/horror/action]

| # | Time | Scene | Shot | Camera | Duration | Description | Characters | Atmosphere | Lighting | SFX | BGM |
|---|------|-------|------|--------|----------|-------------|------------|------------|----------|-----|-----|
| 1 | 0-2s | S-01 Laura卧室 | 全景 | 俯拍+缓推 | 2s | 场景定场 | 环境 | 深夜/晴/月光 | 暖黄烛光(烛台左前)+冷蓝月光(窗外右补)+暗角压暗 | 蜡烛噼啪 | 低沉弦乐pad起 |
| 2 | 2-4s | S-01 Laura卧室 | 近景 | 正面 | 2s | 主要人物状态 | [人物] | 深夜/晴/月光 | 烛光(镜前主)+月光(窗侧补)+发丝光 | 呼吸加重 | 弦乐渐强 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Lighting 列写法规范 (必须三层)
- **主光 (Key Light)**: 主要光源+方向+颜色，如"暖黄烛光(镜前烛台,左前方)"
- **补光 (Fill Light)**: 辅助光源+颜色+方向，如"冷蓝月光(窗外,右侧)"
- **效果 (Effect)**: 暗角/轮廓光/体积光/自发光，如"暗角压暗+紫纹自发光(颈部)"
- ❌ 不够: "烛光" / ✅ 达标: "暖黄烛光(镜前烛台,左前)+冷蓝月光(窗外右补)+暗角压暗"
- **动态来源**: 根据 Scene 环境(室内/室外/白天/夜晚) + 情绪(恐惧→冷光/暧昧→暖光/回忆→褪色泛黄) 推理

## Atmosphere 列写法规范
- **物理天气/时间/光线环境**（非情绪感受），为 Lighting 列提供前置条件
- 格式：`时间+天气+天况`，用"/"分隔
- 示例: "夜晚/晴/月光" / "黄昏/阴/微光" / "深夜/雨/闪电" / "清晨/雾/散射光" / "白天/晴/直射阳光" / "室内/无窗/人工光"
- **动态来源**：根据 Scene 地点(室内/室外) + 剧情时间线(白天/夜晚/清晨/深夜) + 天气(晴/阴/雨/雪/雾/风) 推理
- ❌ 不要写情绪词如"恐怖压抑"、"暧昧紧张"——那些属于 Description 列
- ✅ 应该写物理环境如"深夜/雨/闪电"——这样 Lighting 列才能据此推理光源

## SFX 列写法规范
- 环境音 + 动作音，用"+"分隔
- 示例: "蜡烛噼啪+远处钟声" / "雨声+脚步声" / "翻书声" / "无"
- **动态来源**: 根据 Scene(环境音来源) + Action(动作音来源) 推理

## BGM 列写法规范
- 具体可执行的音乐描述，非情绪标签
- 示例: "低沉弦乐pad起" / "悲伤大提琴独奏" / "无" / "渐强" / "骤停" / "淡出"
- **动态来源**: 根据天气/时间变化 + 本集节奏曲线分配，开场hook用强音乐，对话段可"无"，cliffhanger渐强

## Shot Notes
- **节奏分层**: [开场/中段/结尾的节奏变化]
- **运镜匹配**: [恐怖段/悬念段/情感段对应的运镜策略]
- **景别层次**: [大特写→特写→近景→中景→全景的分布]
- **时空切换**: [场景转换方式+桥接手段]
- **灯光设计**: [全集灯光基调+关键镜头对比，如"暖黄vs冷蓝对比，紫纹自发光贯穿"]
- **音效设计**: [全集环境音主线+关键音效点，如"钟声作为恐惧触发器"]
- **音乐弧线**: [全集BGM起承转合，如"pad起→渐强→骤停(闪回)→弦乐爆发(cliffhanger)"]
- **AI指令颗粒度**: [特效/VFX参数，如紫纹=位置+颜色+脉动频率]
- **情绪递进**: [情绪起点→终点，如何用镜头语言"看见"]
- **运镜种类统计**: 推/侧面/正面/仰拍/俯拍/跟拍/拉/摇 = [N]种
```

## 批量生产模式 (execute_code)

当需要快速生成多集完整内容时使用 `execute_code` 批量生成：

```python
import os

base = "/path/to/project"

# 单集批量写入（剧本 + 分镜 + 提示词）
for ep, (script, sb, pr) in episodes.items():
    for fname, content in [
        (f"script/EP-{ep:02d}.md", script),
        (f"storyboard/EP-{ep:02d}.md", sb),
        (f"prompts/EP-{ep:02d}.md", pr),
    ]:
        with open(f"{base}/{fname}", "w", encoding="utf-8") as f:
            f.write(content)
```

**批量分镜最佳实践（v3.4 ⭐ 2026-05-15 Carmilla v2 验证）**：
- **2-3 集合并生成**：用户确认"后面可以尝试2集或3集合一起去生成"。主模型单次输出 20-30K chars 不中断，是最佳批量粒度。
- **写前必做**：先读剧本 → 分析集类型(恐怖/对峙/亲密/揭示/调查) → 确定节奏/运镜/灯光策略 → 再生成。
- **写后必做**：每集内联 Storyboard-Aligner 自审（6维度评分），≥80 分 PASS。
- **详细实战模式**：见 `references/storyboard-bulk-generation-patterns.md`（集类型分类、运镜策略、节奏模式、常见扣分项）

**批量模式 vs 多 Agent 模式的选择：**
| 场景 | 推荐方式 |
|------|---------|
| 多集快速出稿 | execute_code 批量生成 |
| 单集精雕细琢 | delegate_task 独立审核员 |
| **最佳实践** | 批量生成初稿 + 独立审核员逐集审 + 不通过就重写 |

## 大规模批量生成检查清单 (v2.4 ⭐ 2026-04-30 Count of Monte Cristo 验证)

> 当一次性生成 10+ 集时，必须执行以下步骤，否则会出现文件缺失（如 EP-20 prompts 漏写）。

**生成后必做验证（在继续工作台之前）：**

```python
import os
base = "/path/to/project"
for i in range(1, 37):
    ep = f"EP-{i:02d}"
    for subdir in ["script", "storyboard", "prompts"]:
        fp = f"{base}/{subdir}/{ep}.md"
        if not os.path.exists(fp):
            print(f"MISSING: {subdir}/{ep}.md")
```

**分镜批量生成标准化参数（36集验证）：**
| 参数 | 标准 | 范围 |
|------|------|------|
| 镜头数 | 18 | 16-20（氛围16-18 / 标准18-20 / 高潮20-24） |
| 总时长 | 70s | 固定 |
| 正面镜头比例 | 80-94% | 表情特写为主时偏高可接受 |
| 运镜种类 | ≥5种 | 推/拉/跟拍/俯拍/俯拍/过肩/固定 |
| 时长校验 | 必须等于70s | 每集 Shot Notes 末尾必须有校验行 |

**Prompts 批量生成标准化结构（每集必含）：**
1. `## Visual Asset References` — 本集角色外观 + 场景列表
2. `### Frame N: time Shot` — 每张图的完整 Prompt（18-20帧）
3. `## Shot Notes` — 场景/色调/情感弧线/关键道具/服装注意/对白

**批量生成后缺失处理流程：**
1. 运行验证脚本（见上）
2. 发现缺失 → 立即读取对应 script/EP-XX.md
3. 手写补齐 storyboard 和 prompts（不走 delegate_task，速度更快）
4. 重新验证确认全部存在 → 才能进入工作台阶段

## 生产工作台页面 (Index Page) — v4.0

> 将三件套 MD 文件转换为交互式 SPA（单 HTML 文件），用于管理 AI 生图/视频流程、追踪进度、一键复制 Prompt。
> **三文件架构 v4.0**：`generate_index.py`（MD → JSON） + `workbench/`（固定模板 + 构建脚本）
> 详细规范见：`drama-prompts/workbench/` 或技能 `short-drama-production-index`

### Step 1: `generate_index.py` — MD → JSON 解析器

> ⭐ **推荐使用模板**：`templates/generate_index.py`（已包含双格式解析 + VO-only 支持）
> 复制到项目根目录即可运行：`cp templates/generate_index.py /path/to/project/ && python3 generate_index.py`

**核心结构**（关键陷阱已内联到解析器中）：

```python
#!/usr/bin/env python3
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))

def read(path):
    with open(os.path.join(BASE, path), 'r', encoding='utf-8') as f:
        return f.read()

# 解析函数：parse_script, parse_storyboard, parse_prompts, parse_characters, parse_manifest
# 关键修复点：
# 1. 正则用 (?=\n## [^#]|\Z) 而非 (?=##|$)，否则 ### 会被误匹配
# 2. Scene Breakdown 列数 >= 2（不是5），Key Dialogue >= 2（不是 ==2）
# 3. Cliffhanger 兼容 "## Cliffhanger / 终局" 后缀格式
# 4. Voiceovers 初始化空列表，VO-only 集不会 KeyError

def main():
    data = {'project': 'ProjectName', 'total_episodes': 33, 'episodes': [], 'characters': [], 'manifest': {}, 'scenes': [], 'props': []}
    
    # 加载 manifest, scene_prop_data.json
    if os.path.exists('visual_assets/manifest.md'):
        data['manifest'] = parse_manifest(read('visual_assets/manifest.md'))
    if os.path.exists('scene_prop_data.json'):
        with open('scene_prop_data.json', 'r', encoding='utf-8') as f:
            sp_data = json.load(f)
        data['scenes'] = sp_data.get('scenes', [])
        data['props'] = sp_data.get('props', [])
    
    # 遍历 script/ 目录，按 EP 解析三件套
    script_dir = os.path.join(BASE, 'script')
    for fname in sorted(os.listdir(script_dir)):
        if not fname.endswith('.md'): continue
        ep_id = fname.replace('.md', '')
        episodes.append({
            'id': ep_id, 'title': title,
            'script': parse_script(read(f'script/{fname}')),
            'storyboard': parse_storyboard(sb_md),
            'prompts': parse_prompts(pr_md),
        })
    
    # 输出 JSON
    with open('project_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

**完整代码见模板**：`templates/generate_index.py`（含全部解析器实现 + 正则模式速查表）

> ⭐ **数据提取原则（用户偏好）**：剧本对白/VO/Cliffhanger 等复杂结构化数据 → **主模型直接提取**，不用正则。规则格式（分镜 Markdown 表格、manifest 表格）→ 正则脚本。

### Step 2: 运行解析

```bash
cd /path/to/project
python3 generate_index.py
# → 生成 project_data.json
```

### Step 3: 复制工作台风架 + 构建

```bash
# 从 drama-prompts 复制 workbench 到项目
cp -r ~/.hermes/tasks/drama-prompts/workbench/* /path/to/project/

# 构建
cd /path/to/project
python3 build_html.py
# → 生成 index.html（~635KB，单文件自包含，内含所有数据分块）
```

**v4.0 工作台架构**：

| 文件 | 角色 | 大小 |
|------|------|------|
| `template.html` | 固定 SPA 应用模板，含 9 Tab + 附件预览 + 全量可编辑 + 导入/导出 | ~32KB |
| `build_html.py` | 构建脚本：读取 JSON → 分块（~30KB/块）→ 注入 → 输出 index.html | ~2KB |
| `project_data.json` | 数据源（`generate_index.py` 生成） | 项目相关 |
| `index.html` | 最终产物，单文件自包含，双击即用 | ~635KB |

**9 个 Tab**：📊 仪表盘 / 🎬 分镜 / 📝 剧本 / 👤 角色 / 🏰 场景 / 🧰 道具 / 🖼️ 图片Prompt / 🎞️ 视频Prompt / 📁 素材库

**核心特性**：
- **全量可编辑**：所有文本字段 `contenteditable`，失焦自动存 localStorage，刷新不丢
- **💾 保存 JSON**：合并编辑回 JSON 后下载，替换后 `python3 build_html.py` 重新生成
- **📂 加载 JSON**：选择本地 JSON 文件导入替换
- **数据分块注入**：JSON 按 ~30KB 分块存入 `<script type="application/json" class="__data_chunk__">` 标签，JS 收集拼接后解析
- **移动端适配**：侧栏隐藏、Tab 横滑、附件缩略图缩小

### 正则解析模式速查表

| 解析目标 | 正则锚点 |
|----------|---------|
| 场景分解 | `## Scene Breakdown\n(.+?)(?=\n## [^#]|\Z)` |
| Key Dialogue | `## Key Dialogue\n(.+?)(?=\n## [^#]|\Z)` |
| 分镜表 (Key Frames) | `## Key Frames\n(.+?)(?=\n## [^#]|\Z)` |
| Image Prompts | `### Frame (\d+): (.+?)\n\*\*Prompt:\*\*(.*?)` |
| Video Prompts | `### Shot (\d+): (.+?)\n\*\*Prompt:\*\*(.*?)` |
| 角色 (H2 + attrs) | `## (.+?)\n(.+?)(?=## |\Z)` |

### 打包交付

```bash
tar --exclude='__pycache__' -czf /path/to/desktop/project-name.tar.gz -C /path/to project-name/
```

### 常见陷阱

**解析器陷阱（⭐ 必须遵守）**：
1. **正则截断** — 所有 `parse_script` / `parse_storyboard` 正则必须用 `(?=\n## [^#]|\Z)` 而非 `(?=##|$)`，否则 `###` 会被误匹配截断
2. **列数动态检测** — Scene Breakdown/Key Dialogue/分镜表列数必须用 `>= 2`（不是 `==` 或 `>= 5`），动态映射 headers
3. **Cliffhanger 后缀** — 正则 `## Cliffhanger[^\n]*\n` 兼容 `/ 终局` 等后缀
4. **Voiceovers 初始化** — result 字典必须包含 `'voiceovers': []`，VO-only 集不会 KeyError
5. **manifest.md 分区段解析** — 按 `##` 大标题切分区段独立解析，避免全局扫描导致的跨区污染

**工作台 v4.0 陷阱**：
- **JSON 格式必须含 `project` 和 `total_episodes`** — 标题从 `data['project']` 读取（不是 `manifest.title`）
- **不要硬编码列数** — 分镜表头动态解析（8列/12列变化频繁）
- **修改 JSON 后必须重新运行 `build_html.py`** — 工作台渲染的是嵌入的 JSON 快照
- **`generate_index.py` 提取剧本对白用主模型** — 正则解析容易把动作描述混入对白（v3.1 实测 3 轮才调通）

## 注意事项

### 1. AI 审核的局限性
- Aligner 本身是 AI，可能僵化执行规则
- 可能对"格式正确但创意平庸"的剧本给 PASS
- **必须人工最终把关**

### 2. 昂贵的审核循环
- FAIL → 修改 → 再 FAIL 消耗大量 Token
- 同一问题反复 FAIL 超过 2-3 次时立即人工介入

### 3. 记忆污染风险
- 手动修改文档会导致 Recorder 记录过时
- **修改文档后需要手动更新 script.progress.md**

### 4. 风格漂移
- 长时间对话后可能忘记上下文
- 需要定期在 context 中重申创作法则

### 5. 视觉资产管理（三文件架构）
- **三文件各司其职** — `characters.md`（角色身份）、`scene_prop_data.json`（场景/道具 Reference）、`manifest.md`（视觉规则）
- **manifest.md 只保留不可替代内容**：服装场景映射、表情关键词、色调/光影/构图规则
- **角色外观改 → 只改 `characters.md`**
- **场景/道具改 → 只改 `scene_prop_data.json`**
- **服装/情绪/色调改 → 只改 `manifest.md`**
- 新角色首次出场时，同时更新三文件（characters.md 身份 + manifest.md 服装/表情 + scene_prop_data.json 如需要新场景）

---

## Drama Studio 集成参考

> Drama Studio 是 drama-team 的 Web UI 扩展（11 阶段流水线），项目位于 `~/.hermes/tasks/drama-studio/`。
> 启动：后端 `server/index.ts`（端口 3000），TapNow 前端端口 5176。
> AI 模型默认 qwen27b-awq（本地）。详见 `DESIGN.md`。

**核心架构**：
- 编剧层 7 阶段（输入处理 + 标准 6 阶段）→ 制作层 4 阶段（生图/生视频/配音/合成）→ 交付
- MCP 集成（`services/mcp.ts`，并发 3），全局资源一次生成全剧复用
- TapNow 为 state-based 无 React Router，四级下钻有返回导航，新建必须输入入口
- 工作流：全局资源(角色/场景/道具图)生一次 → 每集独立：剧本→分镜→Prompt→优化→生图→生视频→单集合成
- 端口：后端 3000，经典前端 5174，Luma 5175，TapNow 5176

## GitHub 同步

- 技能库仓库：`https://github.com/husw725/drama-prompts/`
- 同步：`git add -A && git commit -m "update" && git push`
- 读者人设更新参考：本技能 `## 审核员系统` 章节的国际化人设切换表

## 相关技能

- `hermes-agent` — Hermes Agent 配置与调试
- `writing-plans` — 实施规划与任务分解
- `novel-to-short-drama-adaptation` — 小说改编短剧流程
- `short-drama-production-index` — 短剧工作台 JSON/HTML 生成
- `drama-studio` — 11 阶段 Web UI 短剧制作系统
- `seedance2-short-drama-workflow` — Seedance 2.0 短剧制作工作流
- `video-dubbing-indextts2` — IndexTTS 2.0 翻译配音工作流
