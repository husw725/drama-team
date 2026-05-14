---
name: hermes-short-drama-team
description: 短剧编剧全流程系统 — 严格按集串行生成，含剧集连续性追踪、伏笔管理、视觉一致性管控与独立审核机制
version: 2.7.0
author: Hermes Agent + User
license: MIT
metadata:
  hermes:
    tags: [Short-Drama, Scriptwriting, Creative-AI, Visual-Consistency, Continuity, Foreshadowing, Sequential-Generation]
    related_skills: [hermes-agent, writing-plans, novel-to-short-drama-adaptation, short-drama-production-index]
---

# Hermes Agent 短剧编剧团队 v2.7

> 短剧编剧全流程系统：从小说/Idea到剧本、分镜、AI生图Prompt。
> **v2.0 新增**：视觉资产清单 + Prompt 强制注入 + 审核员一致性检查。
> **v2.2 新增**：场景/道具 Reference 体系 — `[ref: S-XX]` 标记。
> **v2.3 新增**：三文件架构 — `characters.md` + `scene_prop_data.json` + `manifest.md`。
> **v2.4 🔥 重大变更**：**严格按集串行生成**，新增 `continuity.md` 连续性追踪 + 伏笔回收管理 + 跨集交接协议。
> **v2.5 🔥 缺陷修复**：输入处理标准化（小说/PDF/Idea）+ 上下文截断策略 + 读者反馈模拟（三虚拟读者）+ 质量回退链 + 视觉资产变更检测 + 串行/并行明确划分 + 时间预算管理 + 文件依赖关系图。
> **v2.6 🔥 生产验证**：批量委托策略（主Agent逐集精修）+ 审核不可跳过 + 子Agent中断恢复。
> **v2.7 🔥 编剧学习系统**：剧本版本对比→分析修改逻辑→提炼风格规则→更新Prompt。编剧修订不仅是更新文件，更是优化AI编剧行为的闭环学习机制。

## 子 Agent 委托策略（v2.6 ⭐ 2026-05-12 Lady Audley's Secret 验证）

> **核心缺陷修复**：一次性委托 24+ 集给子 Agent 导致 token 耗尽/中断/跳过审核。

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
| **Script Aligner** | 独立审核剧本/分镜/Prompts，返回 PASS/FAIL（含视觉一致性+跨集连续性检查） |

### 核心机制

1. **🔥 严格按集串行生成（v2.4 重大变更）** — 不使用多子Agent并行。主Agent逐集完成：EP-01剧本→审核→分镜→Prompts→提取连续性信息→EP-02...。避免会话隔离导致的叙事断裂。
2. **🔥 连续性追踪文件 `continuity.md`（v2.4 新增）** — 每集完成后自动更新，记录伏笔、悬念、角色状态变化，下一集开始前强制读取。
3. **六阶段创作流程** — 大纲 → 人物 → **视觉资产清单** → **按集循环（剧本→分镜→Prompts）**
4. **视觉资产驱动** — 所有 Prompts 强制注入视觉资产清单中的角色描述，确保跨集一致性
5. **ReAct 循环优化** — Aligner 审核（含跨集连续性），不达标返回修改建议，循环直到通过
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
    │  Aligner审      Aligner审     Aligner审                  │
    │  (含连续性)     (含连续性)   (含连续性)                  │
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
│    - 记录本集结尾 Cliffhanger                                     │
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
Carmilla化为雾气消失，Laura颈间的咬痕开始发出紫色光芒。
Laura对着空房间说："你到底是谁？"

**下一集（EP-03）必须：**
1. 开篇直接承接：Laura触摸发光的咬痕
2. 揭示或推进：紫光与Carmilla的联系
3. 建立新的悬念

---

## 角色当前状态 (Character State)

| 角色 | 当前状态 | 变化时间 |
|------|---------|---------|
| Laura | 颈间有紫色发光咬痕，恐惧但开始调查 | EP-01至今 |
| Carmilla | 身份神秘，已吸血一次，表现出矛盾情感 | EP-02 |
| 父亲 | 发现女儿异常，开始怀疑 | EP-03 |
| 老仆人 | 行为可疑，暗中观察Laura | EP-02 |

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

**三位虚拟读者（每 3-5 集调用一次）：**

| 读者 | 特点 | 关注点 |
|------|------|--------|
| **急躁哥** | 刷短视频，3秒没爽点就划走 | 前3秒有没有冲击力？有没有废话？爽点够不够直接？ |
| **逻辑控** | 剧情党，发现漏洞就弃剧 | 前后矛盾？角色行为不符合动机？时间线对不上？ |
| **情感党** | 为角色上头，意难平会取关 | 角色弧光？核心关系有没有张力？结局满足吗？ |

**调用方式：**

```python
# 每完成 3-5 集后调用一次
from hermes_tools import delegate_task

review_result = delegate_task(
    goal="以虚拟读者视角评审 EP-01 到 EP-05",
    context=f"""
    你是三位虚拟读者的集合体：
    
    1. 急躁哥 — 刷短视频用户，3秒没爽点就划走
    2. 逻辑控 — 剧情党，发现漏洞就弃剧
    3. 情感党 — 为角色上头，意难平会取关
    
    请分别以三个视角评审以下剧本：
    {script_content}
    
    输出格式：
    ## 急躁哥
    - EP-XX: 第X秒划走风险（原因）
    - 建议：...
    
    ## 逻辑控
    - 漏洞1: ...
    - 建议：...
    
    ## 情感党
    - 最上头的场景: ...
    - 意难平: ...
    - 建议：...
    """,
    toolsets=['file']
)
```

**评审触发时机：**
- 每完成 3 集（EP-03, EP-06, EP-09...）自动触发
- 用户手动触发（任何时候）
- 评审结果写入 `review_report.md`，作为后续优化的参考

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
```

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
> 💡 **剧本版本对比与质量审计**（2026-05-13 Carmilla AZ Edit 验证 ⭐ 新增）：
> 当编剧/导演发来修订版剧本，除了更新文件外，**必须做版本对比分析 + 质量审计**：
>
> **Step 1: 版本对比**（用 Python 自动化）
> ```python
> # 读取两版，按集切分
> v1_eps = re.split(r'(?=EPISODE \d+:)', v1_text)
> v2_eps = re.split(r'(?=EPISODE \d+:)', v2_text)
> # 逐集对比：标题、字符数、行数、对白数
> for v1_ep, v2_ep in zip(v1_eps, v2_eps):
>     print(f"EP-XX: V1={len(v1_ep)} chars, V2={len(v2_ep)} chars (delta={len(v2_ep)-len(v1_ep):+d})")
> ```
>
> **Step 2: 质量审计清单**（必查 5 项）：
> | 检查项 | 方法 | 发现案例 |
> |--------|------|---------|
> | **角色名错误** | 扫描 `(CONT'D)` 前的角色名是否与本集实际出场一致 | EP-13 出现 `FATHER (CONT'D)` 但本集无 FATHER |
> | **过度删减** | 单集 Δ > -20% 标记为"过短" | EP-14 仅 881 字（原 1121），EP-15 -25.5% |
> | **结尾缺失** | 检查 V2 末尾是否有 `FADE OUT` / `THE END` | AZ Edit 版结尾只有页码 `50.`，无标准结尾 |
> | **Epilogue 独立** | V1 结尾嵌在 EP-32 vs V2 独立 EPILOGUE 章节 | ✅ AZ Edit 已拆分，结构改进 |
> | **修订说明残留** | V1 末尾是否有 "Revised deficiencies" 等说明 | AZ Edit 已删除，干净 |
>
> **Step 3: 分析编剧修改逻辑**（提炼写入 Prompt 更新）：
> - 句式简化方向（长句→短句，心理描写→动作描述）
> - 格式标准化（CONT'D 使用、页码编号）
> - 语言风格变化（古典腔调→口语化）
> - 节奏调整（删减幅度最大的集 = 编剧认为冗余的段落）
>
> **Step 4: 提意见**（发现不理想的修改要指出）：
> - 关键情感场景过度简化（EP-14 坦白戏、EP-06 两面性对比）
> - 高潮戏压缩（EP-32 最终战从 5831→3107 字，-46.7%）
> - 角色独特性丢失（V1 的 "I trust her not" → V2 "I don't trust her"，哥特腔调变口语）
>
> **Step 5: 学习编剧修改逻辑并更新 Prompt**（⭐ v2.7 新增）：
>
> 编剧的修订不仅是"更新文件"，更是"优化 AI 编剧行为"的机会。每次收到修订版时，都应该：
>
> **学习方向 1：句式风格（Show, Don't Tell）**
> - V1 长复合句 → V2 短动作句是常见模式
> - 例：*"her eyes full of tenderness—nothing like the creature of the night"* → *"her eyes soften"*
> - **更新编剧 Prompt**：加入"短动作驱动"指令：*每个动作不超过2个分句，用独立短句替代复杂从句*
> - **警告**：关键转折点（坦白、最终选择）需要保留足够情感厚度，不能全部简化
>
> **学习方向 2：对话风格一致性**
> - 古典腔调 vs 口语化取决于项目风格
> - 例：*"I trust her not"* (哥特古典) vs *"I don't trust her"* (现代口语)
> - **更新编剧 Prompt**：如果项目是哥特/奇幻，保留 *"archaic phrasing for authority figures"*；如果是现代题材，允许口语化
>
> **学习方向 3：格式标准化**
> - V1 无 CONT'D → V2 68 处 CONT'D（标准剧本格式）
> - V1 无 FADE OUT/THE END → 需要检查 V2 是否补上
> - **更新编剧 Prompt**：强制要求标准好莱坞剧本格式（见下方格式检查清单）
>
> **学习方向 4：节奏感知（从删减幅度反向推导）**
> - 删减最多的集 = 编剧认为"信息冗余、节奏拖沓"
> - EP-05 (-15%)、EP-06 (-19%)、EP-15 (-25.5%)、EP-32 (-46.7%)
> - **更新编剧 Prompt**：加入"节奏紧凑度"指令：*每集信息密度优先，减少重复描述*
>
> **编剧 Prompt 更新模板**（每次修订后更新）：
> ```
> ## 编剧风格指南（vX.X, 更新于 YYYY-MM-DD）
>
> **句式规则**（基于编剧修订版本 vN 分析）：
> - 动作描述：短句优先，每句 ≤ 2 个分句
> - 心理描写：用动作/表情替代内心独白
> - 例外：情感转折点保留 1-2 句长描写作锚点
>
> **对话风格**：
> - [项目风格，如：哥特古典 / 现代口语 / 混合]
> - 权威角色用古语结构（"I trust her not"）
> - 日常角色用自然口语（"I don't trust her"）
>
> **格式要求**：
> - 连续对话必须用 (CONT'D)
> - 集末必须有 FADE TO BLACK 或 FADE OUT
> - 全剧结尾必须有 FADE OUT + THE END
> - 页码不写入剧本（AI 生成不需要）
>
> **节奏规则**（基于删减幅度分析）：
> - 每集信息量 > 情感铺垫量
> - 开场 3 秒直接进入冲突，不接受空镜/铺垫
> - 角色首次出场的视觉描述只写一次（后续用动作替代）
> ```
>
> **版本审计后必须更新的文件**：
> 1. `TASK.md` — 记录"修订版本 vX 分析完成"
> 2. `characters.md` — 如角色对话风格有变化，更新"说话风格"字段
> 3. `manifest.md` — 如视觉风格有变化，更新色调/光影规则
> 4. 编剧 Prompt（本技能 SKILL.md）— 更新"编剧风格指南"章节
> 5. `continuity.md` — 如新增/删除了角色或情节线，更新追踪表
>
> **编剧风格指南持久化**（⭐ v2.7 新增）：
> - 每次分析后，把学到的风格规则写入 `TASK.md` 的 `## Style Guide` 章节
> - 格式：`[YYYY-MM-DD] 编剧 vX 修订 → 短句驱动 + 格式标准化 + 古典腔调保留`
> - 下一次编剧生成时，从 `TASK.md` 读取风格指南注入 prompt

> 💡 **PDF/DOCX 剧本解析路径**（2026-05-13 Carmilla 32集验证 ⭐ 新增）：
> **PDF** → 用 `pymupdf`（fitz），非 `pdftotext`（sandbox 中通常未安装）：
> ```python
> import fitz
> doc = fitz.open('script.pdf')
> text = ''.join(page.get_text() for page in doc)
> # 注意：PDF 提取的文本可能含页码（如 "47." 独占一行），需清理
> ```
> **DOCX** → 用 `python-docx`：
> ```python
> from docx import Document
> doc = Document('script.docx')
> all_paras = [(i, p.text.strip()) for i, p in enumerate(doc.paragraphs) if p.text.strip()]
> # 按 EPISODE 标记切分
> ep_markers = [(num, title, para_idx) for num, title, para_idx in ...]
> ```
>
> **Step 2: 好莱坞剧本解析**（无引号格式 — 角色名一行，对白下一行）
> ```
> LAURA (V.O.)
> Seven days. That's all I have left.
>
> CARMILLA
> (soft, predatory)
> I told you. Fifteen years.
> ```
> - 角色名：全大写，可能含 `(V.O.)` / `(whispering)` 等 parenthetical
> - 对白在角色名下一行（无引号！）
> - parenthetical 行格式：`^\(.*\)$`，需跳过取真正对白
>
> **Step 3: 写入 script/EP-XX.md**（保留 Source Screenplay 代码块 + 提取 Key Dialogue 表格）
>
> **Step 4: 修复 generate_index.py**（常见 3 个问题）：
> 1. **硬编码集数范围** — `for ep_num in range(1, 31)` → 改为 `range(1, N+1)` 或扫描目录
> 2. **缺少文件崩溃** — storyboard/prompts 不存在时 FileNotFoundError → 加 `os.path.exists()` 守卫
> 3. **对白格式不兼容** — 新格式 `| Speaker | EN |` vs 旧格式 `| EN | CN |` → 按表头检测
>
> **Step 5: 生成工作台**
> ```bash
> python3 generate_index.py  # → project_data.json
> python3 build_html.py       # → index.html
> ```
>
> **解析器修复清单（必做）**：
> - `generate_index.py` 的 `main()` 循环：`range(1, 31)` → `range(1, 33)`（或动态）
> - 每个 read() 调用前加 `os.path.exists()` 检查，不存在返回空结构
> - `parse_script()` 支持 `## Source Screenplay` 代码块格式（`meta['screenplay']`）
> - `parse_script()` 的 Key Dialogue 按表头列名自动检测新旧格式
> - `Cliffhanger` 正则用 `(?=\n## |\Z)` 而非 `(?=$)`

> 💡 **逐集精修模式**（2026-04-30 Carmilla 项目验证）：
> 当用户要求"一集一集精修"时，放弃批量脚本，逐集手工精修：
>
> **精修流程（每集独立）：**
> 1. 从 `screenplay_hollywood.txt` 提取单集原文（按 `EPISODE \d+:` 切分）
> 2. 逐行阅读好莱坞格式剧本，理解每个动作/对白/转场
> 3. 按影视节奏分配时间轴（不按固定3秒切分，而是按台词长度+动作复杂度动态分配）
> 4. 写 Scene Breakdown 表格，每行对应一个镜头
> 5. 写入 `script/EP-XX.md`
>
> **精修格式规范：**
>
> **动作描述（中英双语 ⭐ 关键要求）**：
> ```
> 先中文描述（自然语序）/ 后英文原文（好莱坞格式）
> 例：极特写——咬痕破皮，血珠沿苍白脖颈滑落 / EXTREME CLOSE UP – Two fresh bite marks break the skin. A single drop of blood slides down her pale throat.
> ```
> 中文在前，用 `/` 分隔，英文在后保留原文。这样既便于中文团队理解，又保留英文原文供AI生图使用。
>
> **场景标签格式**：
> ```
> S-XX 地点名 [镜头类型]
> 例：S-01 Laura卧室 极特写
>     S-02 古堡走廊 全景
>     S-03 大厅/走廊
> ```
> 镜头类型：极特写 / 特写 / 近景 / 中景 / 全景 / 远景 / 黑屏
>
> **对白格式**：
> ```
> CHARACTER: "EN text" / "中文翻译"
> 例：LAURA: "What… is this?" / "什么……这是？"
>     CARMILLA (V.O.): "Mine… forever." / "我的……永远。"
> ```
>
> **BGM 列（具体音乐描述）**：
> ```
> ❌ 通用描述："紧张"、"悲伤"
> ✅ 具体描述："低频嗡鸣起"、"诡异小提琴起"、"心跳声加速"、"刺耳和弦"、"雾气音效"
> ```
> BGM 描述要具体可执行——像给配乐师的工作指示，不是给观众的情绪标签。
>
> **Cliffhanger（悬念钩子写法）**：
> 每集结尾写一段 Clifhanger 描述（50-150字），包含：
> - 本集最大悬念/转折总结
> - 暗示下一集方向的钩子
> - 关键未解之谜
> 例："Carmilla化为雾气消失，Laura颈间的咬痕开始发出紫色光芒——开场钩子：极特写咬痕+血珠，前3秒直接视觉冲击。"
>
> **时间轴分配原则（不按固定3秒！）**：
> ```
> 纯动作镜头：3-5s
> 对白镜头：4-6s（短句）/ 6-8s（长句）
> 情感转折/揭示：5-8s
> 转场/黑屏：2-4s
> 悬念慢推结尾：最长10s
> ```
> 总时长因集而异（80s-155s），不是固定的70s——"最符合剧本"优先。

**好莱坞剧本转换（`convert_screenplay.py`）：**

> **核心原则：编剧和审核员必须完全独立——审核员不知道编剧是谁、不受编剧影响**

### 流程（v2.4 — 串行模式）

> **关键变更**：不再用多子Agent并行生成。主Agent逐集创作，Aligner 只做独立审核。

1. **编剧（主Agent）** 写完 EP-XX 三件套（script/storyboard/prompts）
2. **派独立审核员**：`delegate_task` 创建子Agent，给它 Aligner v4.0 的完整审核prompt
3. **审核员输出**：PASS ✅ / FAIL ❌ / ⚠️ 需修改
4. **如果 FAIL**：编剧根据审核意见重写，重新派审核员
5. **如果 PASS**：更新 continuity.md → 进入下一集
6. **如果 FAIL 超过 3 次**：人工介入修改

### 审核范围扩展（v2.4 新增）

Aligner 现在增加跨集连续性检查（5分）：

| 检查项 | 标准 | 扣分 |
|--------|------|------|
| 悬念回收 | 是否回收了上一集 Cliffhanger（开篇 3 秒） | -2 |
| 伏笔处理 | 到期伏笔是否处理（查 continuity.md） | -2 |
| 角色状态 | 角色行为是否符合当前状态 | -2 |
| 冲突不重复 | 是否与前 2 集冲突类型不同 | -1 |

### 关键规则
- 审核员 **不读编剧的自检表** — 只看成品本身
- 审核员 **不调用编剧的任何文件** — 只读剧本/分镜/Prompts内容
- 审核员的 context **不包含编剧的意图** — 只看成品质量
- 审核员 **不能给自己打PASS** — 它只审别人写的
- **禁止自批**：编剧写完不能自己说"PASS"，必须派独立Agent审
- 同一集 FAIL 超过 2 次 → 人工介入修改

### delegate_task 调用示例

**编剧调用（v2.4 — 串行模式）：**
```python
# 先读取上下文
continuity = read_file('continuity.md')
outline = read_file('outline.md')
prev_script = read_file('script/EP-02.md') if current_ep > 1 else ''

result = delegate_task(
    goal=f"编写 EP-{ep_num:02d} 剧本",
    context=f"""
    你是主编剧，正在编写第 {ep_num} 集剧本。
    
    【连续性追踪（必须遵守）】
    {continuity}
    
    【大纲中本集梗概】
    {outline_section}
    
    【上一集结尾（必须回收）】
    {prev_cliffhanger}
    
    【视觉资产清单】
    {manifest}
    """,
    toolsets=['file']
)
```

**审核员调用（v2.4 — 含连续性检查）：**
```python
continuity = read_file('continuity.md')

result = delegate_task(
    goal=f"审核 EP-{ep_num:02d} 三件套是否符合 Aligner v4.0 标准",
    context=f"""
    你是Script Aligner审核员。
    审核标准：Aligner v4.0（10项评分 + 跨集连续性5分）
    
    剧本内容：[EP-XX 剧本完整内容]
    分镜内容：[EP-XX 分镜完整内容]
    Prompts内容：[EP-XX Prompts完整内容]
    视觉资产清单：[visual_assets/manifest.md 完整内容]
    
    【连续性追踪（必须检查）】
    {continuity}
    
    特别检查：
    1. 是否回收了上一集 Cliffhanger？
    2. 到期伏笔是否处理？
    3. 角色状态是否一致？
    4. 冲突类型是否与前2集不同？
    """,
    toolsets=['file']
)
```

## 审核员系统 Prompt（Aligner v4.0）

```
你是Script Aligner审核员，职责是审核每一集剧本/分镜/Prompts是否符合竖屏短剧标准。

核心原则：
1. 你是独立审核员，不是编剧——只评不帮改
2. 不要客套，不要"整体不错"——直接指出硬伤
3. 给出具体的扣分理由，不是"扣了但没说为什么"
4. ≥80分 → PASS，70-79分 → ⚠️需修改，≤70分 → FAIL

### 故事审核（9项，95分）
1. 开局钩子（15%）- 前3秒必须有视觉冲击/冲突爆发，-10分
2. 冲突强度（20%）- 每集冲突必须绑定不可逆代价，-15分
3. 悬念钩子（15%）- 结尾必须让观众"不看不行"，-10分
4. 倒计时/紧迫感（10%）- 全剧有明确期限，-5分
5. 人物弧光（10%）- 主角有成长线，反派有悲剧内核，-8分
6. 核心关系利用（10%）- 体现核心关系卖点，-10分
7. 信息揭露节奏（10%）- 暗示→部分揭露→实锤，-8分
8. 重复剧情（5%）- 同模式连续≥2集预警，-5分
9. 视觉记忆点（5%）- 每集至少1个题材标志性镜头，-3分

### 分镜节奏（v2.0）
- 镜头密度：氛围16-18 / 标准18-22 / 恐怖20-24 / 高潮22-25
- 对白节奏：12-15句/集
- 单镜≤5秒（悬念慢推除外最长10秒）
- 正面镜头≤35%
- 运镜种类≥5种

### 视觉一致性检查（v4.0 新增 ⭐）— 5分
**检查项：**
- Prompts 中角色描述是否与 visual_assets/manifest.md 一致（瞳色、发色、服装）
- 多角色同框时是否每个角色都有外观描述
- 场景描述是否与 manifest.md 中的场景视觉匹配
- 道具是否按照 manifest.md 中的描述出现
**扣分规则：**
- 角色外观与清单不一致 → -3分
- 缺少角色外观描述 → -2分
- 场景与清单不一致 → -2分

### 跨集连续性检查（v2.4 新增 🔥）— 5分
**检查项：**
- 是否回收了上一集 Cliffhanger（开篇 3 秒必须承接）
- 到期伏笔是否处理（查 continuity.md 伏笔管理表）
- 角色行为是否符合当前状态（查角色状态表）
- 冲突类型是否与前 2 集不同（查冲突模式记录）
**扣分规则：**
- 未回收上一集悬念 → -2分
- 到期伏笔未处理 → -2分
- 角色状态不一致 → -2分
- 冲突模式与前 2 集重复 → -1分

### 输出格式
## EP-XX 审核报告
### 分镜节奏 | 维度 | 标准 | 实际 | 结果
### 故事审核 | 维度 | 权重 | 判定 | 扣分
### 视觉一致性 | 检查项 | 清单值 | 实际值 | 结果
### 跨集连续性 | 检查项 | 标准 | 实际 | 结果
**总分: XX/110**（故事95 + 视觉5 + 连续性5 = 105，分镜节奏5）
**结论: PASS ✅ / ⚠️需修改 / FAIL ❌**
**修改建议: 1. 2. 3.**
```

## 短剧创作法则

- 每集必有冲突
- 节奏紧凑密集（3秒没冲突就划走）
- 爽点分布合理
- 人物动机清晰
- 伏笔埋设与回收完整
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

## 分镜节奏审核标准（Aligner v2.0）

> 适用于竖屏短剧（70秒/集）的分镜审核，确保镜头密度、景别丰富度、运镜变化符合行业标准。

### 七维评分表

| 维度 | 标准 | 权重 |
|------|------|------|
| 镜头密度 | 氛围16-18 / 标准18-22 / 恐怖20-24 / 高潮22-25 | 20% |
| 冲突密度 | 每2-3秒一个视觉/情绪变化点 | 15% |
| 对白节奏 | 12-15句/集（每4-5秒一句） | 10% |
| 景别丰富度 | 五景均衡分布 | 15% |
| 运镜变化 | 8种运镜组合使用 | 15% |
| 叙事完整度 | 起承转合清晰、场景过渡合理 | 10% |
| 悬念设计 | 结尾有明确cliffhanger钩子 | 10% |

**综合评分 ≥ 80 → PASS**

---

## 故事层面审核标准（Aligner v3.0 → v4.0）

> 分镜节奏只解决"好不好看"，故事标准解决"值不值得看"。

### 1. 开局钩子（Opening Hook）
- **0-3秒** 必须有视觉冲击/冲突爆发/上集悬念回收
- **0-5秒** 观众必须知道本集核心冲突
- 首镜优先：动作/表情特写/上集钩子回收 > 对白 > 场景建立
- ✅ 直接切入关键动作 / ❌ 旁白介绍或空镜铺垫

### 2. 冲突强度（Conflict Stakes）
- 每集冲突绑定不可逆代价（生命/关系/身份/记忆）
- 每3-5集冲突强度必须升级
- ✅ 吸血导致生命倒计时 / ❌ 昼伏夜出的习惯

### 3. 悬念钩子（Cliffhanger）
- 结尾必须让观众"不看不行"
- 钩子包含具体威胁+台词/视觉动作
- ✅ "你的血是我唯一的解药" / ❌ "一切才刚刚开始"

### 4. 倒计时机制（Urgency）
- 全剧必须有明确期限（生命倒计时/诅咒解除/追捕逼近）
- 每3-5集提醒一次（咬痕加深、面色苍白、日期逼近）
- 没有倒计时的短剧 = 观众随时可以停下来

### 5. 人物弧光（Character Arc）
- 主角从A→B状态（懦弱→调查→反抗）
- 反派有悲剧动机+内心挣扎
- 至少1个配角有独立立场和选择

### 6. 核心关系卖点（Core Relationship）
- 明确核心情感关系（双女主/宿敌/禁忌之恋）
- 至少3个名场面：克制/靠近/牺牲
- 必须有"爱恨交织"的张力

### 7. 信息揭露节奏（Reveal Pacing）
| 阶段 | 时间点 | 标准 |
|------|--------|------|
| 暗示 | 前1/4处 | 观众有"不太对"的感觉 |
| 部分揭露 | 中点前 | 观众基本确定，但全貌未明 |
| 实锤 | 1/3-1/2处 | 核心身份/真相彻底曝光 |

### 8. 重复剧情检测（Pattern Check）
- 相同冲突模式连续≥2集 = 预警，≥3集 = FAIL
- 出现预警后，下一集必须换冲突类型或升级

### 9. 视觉记忆点（Visual Anchor）
- 每集至少1个题材标志性视觉镜头
- 观众看完能记住的画面 = 社交传播素材

### 10. 视觉一致性（v4.0 新增 ⭐）
- Prompts 中角色描述与 manifest.md 一致
- 多角色同框时每个角色都有外观描述
- 场景/道具与 manifest.md 匹配

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
描述悬念钩子
```

## 分镜模板

```markdown
# EP-XX: Title - Storyboard
## Key Frames ([N] shots) | Duration: 70s | Type: [atmosphere/standard/horror/action]

| # | Time | Shot | Camera | Duration | Description | Characters | Lighting |
|---|------|------|--------|----------|-------------|------------|----------|
| 1 | 0-2s | 全景 | 俯拍+缓推 | 2s | 场景定场 | 环境 | [光源] |
| 2 | 2-4s | 近景 | 正面 | 2s | 主要人物状态 | [人物] | [光源] |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Shot Notes
- 关键视觉语言说明
- 颜色/光影对比说明
- 运镜种类统计：推/侧面/正面/仰拍/俯拍/跟拍/拉/摇 = [N]种
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

## 生产工作台页面更新

**`build_html.py` 是纯字符串模板（`r"""..."""`），向其中添加 JS/CSS 代码时：**

1. **不要用 f-string！** — JS 代码中的 `{}` 与 Python f-string 冲突，导致大量语法错误
   - ✅ **正确**：`template = r"""..."""` + `template.replace('__JSON_PLACEHOLDER__', json_str)`
   - ❌ **错误**：`f"""..."""` — JS 对象字面量 `{type:'img',idx:i}` 会破坏 Python 语法

2. **插入位置** — JS 函数放在 `</script>` 之前，CSS 放在 `</style>` 之前
   - 使用 `patch` 工具在已有函数后追加（如 `buildCharacters` 之后加 `buildVisualAssets`）

3. **新 Tab 三步走**：
   - ① HTML tab 按钮：`<div class="tab" data-tab="xxx">标签</div>`
   - ② HTML tab 内容区：`<div class="tab-content" id="tab-xxx">`
   - ③ JS 渲染函数：`function buildXxx() {{ ... }}` + 在 `init()` 中调用

4. **数据源** — `generate_index.py` 读取 MD 文件 → 写入 `project_data.json` → `build_html.py` 注入 JS 的 `PROJECT` 全局变量

**`generate_index.py` 新增解析器**：
- 新增 `parse_xxx(text)` 函数，提取结构化数据（表格、列表等）
- 在 `main()` 中调用并写入 `data['xxx']`
- 确保 JSON 可序列化（dict/list/str/int 类型）

**Props 批量注入到帧级 Prompt 的方法**：
- 从 `manifest.md` 解析道具清单（含出现集数）
- 构建 `ep_num → props` 映射
- 每帧 Prompt 用关键词匹配判断是否需要注入对应道具
- 注入位置：`scene: [...]` 描述之后，或用正则插入到 style prefix 后
- **实现方式**：用 `re.sub()` 配合闭包计数器（`counter = {'injected': 0}`）而非 `nonlocal`，因为 `re.sub` 回调函数在独立作用域中 `nonlocal` 会报 SyntaxError

**Hollywood Screenplay 转换**：
- 用 `convert_screenplay.py` 将表格格式剧本转换为好莱坞格式（INT./EXT. scene headings + Action + Character/Dialogue）
- 场景名中文→英文映射表（`SCENE_MAP`）决定 `INT.` vs `EXT.`
- 场景继承：当脚本中后续行只有 `S-01`（无场景名），继承上一行的场景位置
- 输出到 `project_screenplays.json`，由 `generate_index.py` 加载到 `data['screenplays']`
- Screenplay tab 用 `<pre>` + monospace 字体 + `white-space: pre-wrap` 保留格式化

**build_html.py 常见陷阱**：
- JS 函数**必须**插入在正确位置（函数体内部），否则会打断已有函数
  - 之前把 `buildVisualAssets()` 插在了 `buildCharacters` 函数体内，导致 `buildCharacters` 被拆成两半，Python 报 SyntaxError
  - 修复：先删除错误插入的块，再在目标函数结束后重新插入
- 在 `init()` 中调用新函数时，放在 `bindEvents()` 之前（bindEvents 是最后一步）

**好莱坞剧本转换（`convert_screenplay.py`）**：
- 从 `script/EP-XX.md` 表格格式转换为 `INT./EXT. LOCATION - NIGHT` 好莱坞格式
- 关键陷阱：
  - 场景名继承：如果 `S-01` 后面没有场景名，需要携带上一行的场景
  - 表头行会被解析为数据行——跳过 `Scene` / `Action` / `Dialogue` 字段名
  - 对白格式：`Speaker: "EN" / "CN"` 正则提取，`(OS)` / `V.O.` 单独处理
  - 动作描述去除中文前缀：`特写——`、`近景——`、`全景——` 等
  - 场景映射表（`SCENE_MAP`）：中文场景名→英文 `INT./EXT. LOCATION`
  - `INT.` 不要写 `INT..`（`SCENE_MAP` 只存 location，不要在值里含 `INT.` 再拼接）
- 输出 `project_screenplays.json` → `generate_index.py` 加载 → `build_html.py` 的 Screenplay tab 展示
- Screenplay tab 用 `<pre>` + monospace font 保持好莱坞格式缩进

**JS 函数插入常见错误**：
- ❌ 函数插在已有函数中间（如 `buildCharacters` 的 `{ }` 之间）→ 函数被分裂
- ✅ 正确做法：找到函数的闭合 `}}` 之后，再插入新函数
- ✅ 在 `init()` 中调用新函数：插入在 `bindEvents()` 调用之前

## 生产工作台页面 (Index Page)

> 将三件套 MD 文件转换为交互式 SPA（单 HTML 文件），用于管理 AI 生图/视频流程、追踪进度、一键复制 Prompt。
> **双文件架构**：`generate_index.py`（MD → JSON） + `build_html.py`（JSON → SPA）

### Step 1: `generate_index.py` — MD 文件解析器

> ⭐ **推荐使用模板**：`templates/generate_index.py`（已包含双格式解析 + VO-only 支持）
> 复制到项目根目录即可运行：`cp templates/generate_index.py /path/to/project/ && python3 generate_index.py`

```python
#!/usr/bin/env python3
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))

def read(path):
    with open(os.path.join(BASE, path), 'r', encoding='utf-8') as f:
        return f.read()

def parse_manifest(text):
    """Parse visual_assets/manifest.md into structured data."""
    sections = {}
    current_section = None
    current_table = []
    for line in text.split('\n'):
        if line.startswith('## ') and not line.startswith('### '):
            if current_section and current_table:
                sections[current_section] = current_table
            current_section = line[3:].strip()
            current_table = []
            continue
        if line.startswith('### '): continue
        if line.strip().startswith('|') and current_section:
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if len(cells) >= 2 and not all(c == '---' for c in cells):
                current_table.append(cells)
    if current_section and current_table:
        sections[current_section] = current_table
    return sections

def parse_script(md):
    """Parse script .md — supports both Hollywood screenplay (code block) and legacy table format.
    
    ⚠️ 关键修复点（Carmilla 验证）：
    - 所有正则用 (?=\n## [^#]|\Z) 而非 (?=##|$)，否则 ### 小节标题会被误匹配截断
    - Scene Breakdown 列数放宽到 >=2（不是5），因为有些行只有 Time+Action 无对白
    - Key Dialogue 列数用 >=2（不是 ==2），兼容额外列
    - Cliffhanger 标题兼容 "## Cliffhanger / 终局" 等后缀格式
    - Voiceovers 初始化空列表，VO-only 集无 Key Dialogue 也不会报错
    """
    result = {'scenes': [], 'dialogue': [], 'cliffhanger': '', 'voiceovers': []}
    # Hollywood screenplay (code block)
    for m in re.finditer(r'```\n(.*?)\n```', md, re.DOTALL):
        result['screenplay'] = m.group(1).strip()
        for sm in re.finditer(r'(EXT\.|INT\.)\s+(.+?)\s*[-—](.+?)(?:\n|$)', result['screenplay'], re.IGNORECASE):
            result['scenes'].append({'type': sm.group(1), 'location': sm.group(2), 'time': sm.group(3)})
    # Legacy table format — ⚠️ 用 (?=\n## [^#]|\Z) 避免 ### 被误匹配
    for m in re.finditer(r'## Scene Breakdown\n(.+?)(?=\n## [^#]|\Z)', md, re.DOTALL):
        lines = [l for l in m.group(1).split('\n') if '|' in l and '---' not in l]
        for line in lines[1:]:
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 2:
                row = {}
                headers = ['Time', 'Scene', 'Action', 'Dialogue (EN/CN)', 'BGM']
                for i, h in enumerate(headers):
                    row[h] = cols[i] if i < len(cols) else ''
                result['scenes'].append(row)
    # Key Dialogue (may be absent in VO-only episodes) — ⚠️ 用 >=2 非 ==2
    for m in re.finditer(r'## Key Dialogue\n(.+?)(?=\n## [^#]|\Z)', md, re.DOTALL):
        lines = [l for l in m.group(1).split('\n') if '|' in l and '---' not in l]
        for line in lines[1:]:
            cols = [c.strip().strip('"') for c in line.split('|')[1:-1]]
            if len(cols) >= 2: result['dialogue'].append({'EN':cols[0],'CN':cols[1]})
    # Voiceovers (may be the only dialogue in VO-only episodes)
    for m in re.finditer(r'## Voiceovers\n(.+?)(?=\n## [^#]|\Z)', md, re.DOTALL):
        for line in m.group(1).strip().split('\n'):
            vo_m = re.match(r'-\s*VOICEOVER\s*\((\w+)\)\s*(.*)', line.strip(), re.DOTALL)
            if vo_m: result['voiceovers'].append({'speaker': vo_m.group(1), 'text': vo_m.group(2).strip()})
    # Cliffhanger — ⚠️ 兼容 "## Cliffhanger" 和 "## Cliffhanger / 终局" 格式
    m = re.search(r'## Cliffhanger[^\n]*\n(.+?)(?=\n## [^#]|\Z)', md, re.DOTALL)
    if m: result['cliffhanger'] = m.group(1).strip()
    return result

def parse_storyboard(md):
    """Parse storyboard .md — extract shots from Key Frames table.
    
    ⚠️ 关键修复点（Carmilla 验证）：
    - 正则用 (?=\n## [^#]|\Z) 而非 (?=##|$)
    - 列数动态检测：有些项目 7 列（无 Duration），有些 8 列。用 len(cols) >= 7 而非硬编码 >=8
    """
    shots = []
    for m in re.finditer(r'## Key Frames\n(.+?)(?=\n## [^#]|\Z)', md, re.DOTALL):
        lines = [l for l in m.group(1).split('\n') if '|' in l and '---' not in l]
        # 第一行是表头，从第二行开始是数据
        for line in lines[1:]:
            cols = [c.strip() for c in line.split('|')[1:-1]]
            # 动态列数：至少 7 列（# Time Shot Camera Duration Description Characters Lighting）
            if len(cols) >= 7:
                shot = {'#':cols[0],'Time':cols[1],'Shot':cols[2],'Camera':cols[3]}
                shot['Duration'] = cols[4] if len(cols) > 4 else ''
                shot['Description'] = cols[4] if len(cols) > 4 else ''
                shot['Characters'] = cols[5] if len(cols) > 5 else ''
                shot['Lighting'] = cols[6] if len(cols) > 6 else ''
                shots.append(shot)
    return {'shots': shots}

def parse_prompts(md):
    result = {'imagePrompts': [], 'videoPrompts': []}
    for m in re.finditer(r'### Frame (\d+): (.+?)\n\*\*Prompt:\*\*(.*?)(?=\n\n### |\Z)', md, re.DOTALL):
        result['imagePrompts'].append({'frame':int(m.group(1)),'time':m.group(2).strip(),'prompt':m.group(3).strip()})
    for m in re.finditer(r'### Shot (\d+): (.+?)\n\*\*Prompt:\*\*(.*?)(?=\n\n### |\Z)', md, re.DOTALL):
        result['videoPrompts'].append({'shot':int(m.group(1)),'timeRange':m.group(2).strip(),'prompt':m.group(3).strip()})
    return result

def parse_characters(md):
    chars = []
    for m in re.finditer(r'## (.+?)\n(.+?)(?=## |\Z)', md, re.DOTALL):
        attrs = {}
        for am in re.finditer(r'- (.+?): (.+)', m.group(2)):
            attrs[am.group(1)] = am.group(2)
        chars.append({'name': m.group(1).strip(), 'attrs': attrs})
    return chars

def main():
    data = {'episodes': [], 'characters': [], 'manifest': {}, 'screenplays': {}, 'scenes': [], 'props': []}

    # Parse manifest
    if os.path.exists('visual_assets/manifest.md'):
        data['manifest'] = parse_manifest(read('visual_assets/manifest.md'))

    # Load scenes/props from scene_prop_data.json (v2.2+)
    if os.path.exists('scene_prop_data.json'):
        with open('scene_prop_data.json', 'r', encoding='utf-8') as f:
            sp_data = json.load(f)
        data['scenes'] = sp_data.get('scenes', [])
        data['props'] = sp_data.get('props', [])

    # Load screenplays (if convert_screenplay.py has been run)
    if os.path.exists('project_screenplays.json'):
        with open('project_screenplays.json', 'r', encoding='utf-8') as f:
            data['screenplays'] = json.load(f)

    episodes = []
    script_dir = os.path.join(BASE, 'script')
    for fname in sorted(os.listdir(script_dir)):
        if not fname.endswith('.md'): continue
        ep_id = fname.replace('.md', '')
        script_md = read(f'script/{fname}')
        title_m = re.search(r'# ' + ep_id + r':\s*(.+?)(?:\s*\|)', script_md)
        title = title_m.group(1).strip() if title_m else ep_id

        sb_md = read(f'storyboard/{ep_id}.md') if os.path.exists(f'storyboard/{ep_id}.md') else ''
        pr_md = read(f'prompts/{ep_id}.md') if os.path.exists(f'prompts/{ep_id}.md') else ''

        episodes.append({
            'id': ep_id, 'title': title,
            'script': parse_script(script_md),
            'storyboard': parse_storyboard(sb_md),
            'prompts': parse_prompts(pr_md),
        })

    if os.path.exists('characters/characters.md'):
        data['characters'] = parse_characters(read('characters/characters.md'))

    data['episodes'] = sorted(episodes, key=lambda e: e['id'])

    out = os.path.join(BASE, 'project_data.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_img = sum(len(ep['prompts']['imagePrompts']) for ep in data['episodes'])
    total_vid = sum(len(ep['prompts']['videoPrompts']) for ep in data['episodes'])
    print(f"Parsed {len(data['episodes'])} episodes, {len(data['characters'])} characters")
    print(f"Total: {total_img} image prompts, {total_vid} video prompts")
    print(f"Scenes: {len(data['scenes'])}, Props: {len(data['props'])}")
    print(f"JSON saved to {out} ({os.path.getsize(out)/1024:.0f}KB)")

if __name__ == '__main__':
    main()
```

### Step 2: 运行解析

```bash
cd /path/to/project
python3 generate_index.py
# → 生成 project_data.json
```

### Step 3: `build_html.py` — SPA 生成器

**关键技术点**：
1. **分镜 (storyboard)** — 分镜表 + 进度追踪
2. **剧本 (script)** — 场景分解 + 对白 + 悬念
3. **Prompt (prompts)** — Image/Video Prompts + 批量复制
4. **视觉资产 (visual_assets)** — manifest.md 表格展示
5. **Screenplay (screenplay)** — 好莱坞格式剧本 + 集数切换
6. **角色 (characters)** — 角色设定一览

**关键技术点**：
- **不要用 f-string！** — 用 `r"""..."""` + `str.replace()` 注入数据，避免 JS `{}` 与 Python 冲突
  ```python
  template = r"""<!DOCTYPE html>...const PROJECT = __JSON_PLACEHOLDER__;...</html>"""
  html = template.replace('__JSON_PLACEHOLDER__', json.dumps(data, ensure_ascii=False))
  ```
- `build_html.py` 将 `project_data.json` 通过 `json.dumps` 注入 JS 的 `PROJECT` 全局变量
- **纯前端 SPA**：零依赖，单 HTML 文件，Tab 切换纯 JS 实现
- **localStorage 状态管理**：进度追踪、Prompt 编辑、图片状态持久化到浏览器 localStorage
  ```js
  // 示例：持久化帧进度
  function saveProgress() {{
      localStorage.setItem('project_progress', JSON.stringify(progressState));
  }}
  function loadProgress() {{
      const saved = localStorage.getItem('project_progress');
      return saved ? JSON.parse(saved) : {{}};
  }}
  ```

### 新增 Tab 三步走

1. **HTML tab 按钮**：`<div class="tab" data-tab="xxx">标签</div>`
2. **HTML 内容区**：`<div class="tab-content" id="tab-xxx"><div id="xxxContainer"></div></div>`
3. **JS 渲染函数**：`function buildXxx() {{ ... }}` + 在 `init()` 中调用（放在 `bindEvents()` 之前）

### `generate_index.py` 新增解析器

- 新增 `parse_xxx(text)` 函数，提取结构化数据（表格、列表等）
- 在 `main()` 中调用并写入 `data['xxx']`
- 确保 JSON 可序列化（dict/list/str/int 类型）

### 正则解析模式速查表

| 解析目标 | 正则锚点 |
|----------|---------|
| 场景分解 | `## Scene Breakdown\n(.+?)(?=##|$)` |
| Key Dialogue | `## Key Dialogue\n(.+?)(?=##|$)` |
| 分镜表 (Key Frames) | `## Key Frames\n(.+?)(?=##|$)` |
| Image Prompts | `### Frame (\d+): (.+?)\n\*\*Prompt:\*\*(.*?)` |
| Video Prompts | `### Shot (\d+): (.+?)\n\*\*Prompt:\*\*(.*?)` |
| 角色 (H2 + attrs) | `## (.+?)\n(.+?)(?=## |\Z)` |

### 打包交付

```bash
tar --exclude='__pycache__' -czf /path/to/desktop/project-name.tar.gz -C /path/to project-name/
```

### 常见陷阱
**批量生产陷阱**
- **tool call 超时卡住** — `Still working... (18min elapsed, iteration 23/60)` 表示模型响应失败/断流。遇到此情况：**立即终止当前调用**，用 `read_file` 检查文件是否写入成功，如未完成则重新生成。不要让单个 tool call 运行超过 5 分钟无响应。（2026-04-30 Count of Monte Cristo EP13 遭遇）
- **文件遗漏不报** — 批量生成多集时（10+集），单次 write_file 可能静默失败或中断。生成后**必须运行完整性校验脚本**（见上节"大规模批量生成检查清单"），逐个 EP 检查 script/storyboard/prompts 三件套是否齐全。漏掉一集（如 EP-20）会导致最终工作台数据缺失。

**常见陷阱**
- **JS 函数插入位置** — 必须放在目标函数闭合 `}}` 之后，不要插在已有函数体内（会分裂函数导致 SyntaxError）
- **`re.sub()` 回调计数** — 用 `counter = {'injected': 0}` 字典而非 `nonlocal`，因为回调在独立作用域
- **帧时间清洗** — 中文后缀如 `46-50s 近景` 需要 `clean_time()` 提取纯数字
- **`init()` 调用顺序** — 新渲染函数放在 `bindEvents()` 之前调用
- **`parse_table` min_cols 陷阱** — Key Dialogue 表格只有 2 列（`| EN | CN |`），如果 `parse_table` 要求 `≥3` 列会导致对白全量为空。**必须设 `min_cols=2`**（2026-04-30 Carmilla 项目修复：对白从 0 → 413 条）
- **表头破折号行** — Markdown 表头分隔行（如 `|-------|--------|...|`）会被解析为数据行，渲染成 `-------` 垃圾数据。过滤逻辑：`if all(re.match(r'^[-_]{2,}$', c) for c in cells): continue`
- **分镜表格列数不固定** — 有些项目分镜是 7 列（无 Duration），有些是 8 列。解析器必须动态检测列数而非硬编码 `>=8`，否则全量分镜被跳过
- **数据层更新 ≠ 工作台更新** — 修改 `project_data.json` 后必须重新运行 `python3 build_html.py`，否则 index.html 仍是旧数据。工作台渲染的是嵌入的 JSON 快照，不是实时读取 JSON 文件
- **纯 VO 集无对白表格** — 有些集（如 Count of Monte Cristo EP-05）只有旁白（Voiceover），无 Key Dialogue 表格。解析器必须处理 `## Key Dialogue` 缺失的情况，否则报错
- **剧本格式不统一** — 部分剧本含 `## Source Screenplay` + 代码块格式，部分含 `## Scene Breakdown` + 表格格式。`generate_index.py` 的 `parse_script()` 必须同时支持两种格式，否则部分集丢失数据
- **manifest.md 解析跨区污染** — 用 `"服装指南" in md[:md.find(m.group(0))]` 全局扫描会导致表情/规则区段被误判为服装数据。表现：Bandit Leader 服装表混入道具数据，色调规则表被当服装。**修复：按 `##` 大标题切分区段** (`wardrobe_start = md.find('## 服装指南')`, `expression_start = md.find('## 表情/姿态关键词库')`)，每区段独立解析
- **角色名正则含特殊字符** — `Haydée` 的 `é` 不被 `Haydee` 匹配导致服装数据丢失。正则需覆盖带/不带重音符号变体: `r'(Haydé|Haydée)'`
- **解析器与源文件标题不一致** — 代码 `md.find('## 表情/姿态库')` 但源文件标题是 `## 表情/姿态关键词库` → 表情库全量丢失。提供 fallback 链: `md.find('...关键词库') or md.find('...库')`
- **manifest.md 源文件被脏数据污染** — 早期 AI 生成可能将道具表、规则表混入服装表（如 Bandit Leader 下出现 34 条道具行）。**修复：人工检查 manifest.md 各角色章节是否只有 `| 阶段/场景 | 服装 |` 格式的行，非角色行全部删除**

**解析器致命陷阱（Carmilla 项目全量验证 ⭐ 最高优先级）**：
- **正则截断陷阱** — 所有 `parse_script` / `parse_storyboard` 的正则必须用 `(?=\n## [^#]|\Z)` 而非 `(?=##|$)`。原因：`(?=##|$)` 会匹配到 `###` 小节标题（如 `### Frame 1:`），导致 Section 内容被截断。Carmilla 项目中此 Bug 导致 Scene Breakdown 只解析到第一行、场景/道具全量丢失。
- **Scene Breakdown 列数陷阱** — 默认要求 `len(cols) >= 5` 会漏掉只有 2-3 列的行（纯动作无对白）。**必须用 `>= 2` 并动态映射 headers**，否则 BGM 列、对白列缺失的行全部被跳过。
- **Key Dialogue `== 2` 陷阱** — 用 `len(cols) == 2` 要求恰好两列，但如果表格有额外空格或列数偏移，对白全量丢失。**必须用 `>= 2`**。
- **Cliffhanger 标题后缀陷阱** — 部分集用 `## Cliffhanger / 终局` 等后缀格式。正则 `## Cliffhanger\n` 无法匹配，改为 `## Cliffhanger[^\n]*\n`。
- **Voiceovers 未初始化陷阱** — 默认 `result` 字典不含 `voiceovers` 键，VO-only 集调用时 `KeyError`。**必须在 result 初始化时包含 `'voiceovers': []`**。
- **分镜列数硬编码陷阱** — 默认 `len(cols) >= 8` 跳过 7 列分镜表。改为动态检测 `>= 7` 并条件赋值。
- **parse_script 重复代码陷阱** — 模板中有两段 `Key Dialogue` 和 `Cliffhanger` 代码（第一段后已有 `return`，第二段永远不会执行）。清理死代码，确保只有一个 return。

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

## Drama Studio 系统架构 (v2026-05-09 新增)

> 将 drama-team 的 6 阶段编剧流程扩展为 **12 阶段端到端短剧生成系统**，从用户输入小说/Idea 到最终成片输出。
> 项目位于 `~/.hermes/tasks/drama-studio/`，设计文档见 `DESIGN.md`。

### 架构演进

```
drama-team (6 阶段): 大纲 → 人物 → 视觉资产 → 剧本 → 分镜 → Prompts
                              ↓
Drama Studio (12 阶段): 输入处理 → 编剧层(7) → 制作层(4) → 交付
```

### 11 阶段全貌 (v2026-05-09 → v2026-05-10 确认: 11 阶段，无 input_analysis/dubbing)

> **关键合并**：`input_analysis` 合并到 `ip_analysis` — 第一阶段 system prompt 增加"如果用户提供小说，先做内容分析"逻辑，不单独成一阶段。

```
📝 输入 + 编剧层 (全局，只跑一次)
  1️⃣  ip_analysis       IP 世界观分析（含小说内容解析）
  2️⃣  outline           三幕结构大纲、分集梗概
  3️⃣  characters        角色设定（外貌/性格/关系）
  4️⃣  visual_assets     视觉风格定义（色调/场景/参考）

🎬 分集层 (按集 EP-01, EP-02...)
  5️⃣  script           单集剧本 — ⚠️ Aligner 审核 (≥80 PASS)
  6️⃣  storyboard       分镜表 — ⚠️ Aligner 审核
  7️⃣  prompts          AI 生图 Prompt — ⚠️ Aligner 审核
  8️⃣  prompt_optimization 英文→中文 (Seedance 14 项检查)

🎨 制作层 (按集串行)
  9️⃣  image_gen        Dreamina text2image（角色/场景/特写，全局复用）
  🔟  video_gen        Seedance 2.0 multimodal2video（自带声音！）
  1️⃣1️⃣  assembly       FFmpeg 拼接成片
```

> ⚠️ **关键设计变更 (2026-05-09)**：
> - **去掉配音阶段** — Seedance 2.0 原生生成带声音的视频，无需 IndexTTS 单独配音
> - **新增 prompt_optimization 阶段** — 编剧层的英文 prompt 必须经 AI 转为 Seedance 2.0 合规格式（14 项官方检查清单），这是生视频质量的门控
> - **image_gen 不再按集** — 基础图（角色肖像+场景+特写）全局复用，只跑一次

### 前端设计 (Vite 5174)

三栏布局 + 底部面板：
- **左侧**：项目列表（名称/状态/进度）
- **主区**：无限画布（节点编辑器），节点颜色状态：⚪pending → 🔵running → 🟢done → 🔴error → 🟡outdated
- **底部**：Tab 切换（📄内容查看 / 💬AI 对话修改 / 📋日志 / ▶️预览）

### 后端架构 (Express 3000)

```
server/
  index.ts              # Express + WebSocket (端口 3000)
                        # .env 加载: process.loadEnvFile() (Node 22 原生)
  ws.ts                 # wsBroadcast() 实时推送
  prompts.ts            # 各阶段 System Prompt（从 drama-team 技能提取）
  ai.ts                 # callAI() — vLLM OpenAI API (qwen27b-awq)
  services/
    pipeline.ts         # Pipeline orchestrator: runPhase(), alignerLoop()
    mcp.ts              # 🔥 MCP Client (Streamable HTTP, v2026-05-11)
                        #   Session 管理 + JSON-RPC 调用 + 异步轮询队列
                        #   seedanceGenerateVideo / getTaskById
    mcp-parser.ts       # 🔥 镜头/文本解析器
                        #   parseVideoShots() / tryParseJson() / cleanText()
    video_gen.ts        # 视频生成 (MCP seedanceGenerateVideo → 占位降级)
    image_gen.ts        # 生图 (预留后续 MCP 生图)
    assembly.ts         # FFmpeg 合成
  routes/
    project.ts          # CRUD: /api/projects
    phase.ts            # 执行: /api/phases/:id/run, /cancel, /order
  .env                  # 🔥 MCP_URL / MCP_AUTH_TOKEN / LLM 配置
shared/
  types.ts              # ProjectData, PhaseStatus, PhaseName
```

**🔥 MCP 集成 (v2026-05-11)**

视频生成已从 CLI 调用迁移至 MCP 接口。核心模块：

| 文件 | 职责 |
|------|------|
| `server/services/mcp.ts` | MCP 客户端：Session 管理、JSON-RPC 调用、异步任务轮询（并发 3 个 shot） |
| `server/services/mcp-parser.ts` | 解析器：`parseVideoShots()` 从 prompt 提取镜头、JSON 提取、文本清洗 |
| `server/services/video_gen.ts` | 视频服务：MCP 优先 → FFmpeg 占位降级 |
| `server/.env` | 配置：`MCP_URL` + `MCP_AUTH_TOKEN`，测试服/正式服一键切换 |

**MCP 服务器信息：**
- 测试服：`https://kkshort-adsmanager-dev.mikktv.xyz/adsmanager/mcp`
- 协议：MCP 2025-03-26 (Streamable HTTP)，需 `Mcp-Session-Id` 维持会话
- 工具：`seedanceGenerateVideo`（异步视频生成，全字段 required）+ `getTaskById`（轮询）
- 生图工具：待后续上线，架构已预留

**API 端点：**
- `GET /api/mcp/status` — 连通性检查，返回 `{configured, connected, tools: [...]}`

### 关键技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| LLM | vLLM + Qwen3.6-27B (qwen27b-awq) | 本地运行，编剧质量足够 |
| 生图 | Dreamina CLI | 多账号并行，角色一致性 |
| 视频 | Seedance 2.0 | 关键帧引导法 |
| 配音 | IndexTTS 2.0 | 零样本声音克隆+情感控制 |
| 合成 | FFmpeg | 成熟、灵活 |
| 前端 | Vite + 纯 TS | 轻量，不依赖 React/Vue |
| 存储 | 先内存 Map → 后期 SQLite | 快速迭代 |

### 已知 Bug / 待修复

- **Storyboard 0 字符问题** (2026-05-09 发现)：Storyboard 阶段运行 6.7 分钟但返回 0 字符。根因：上游上下文（ip_analysis+outline+characters+visual_assets 合计 ~10KB+）过长导致 AI 超时或返回空。修复方向：`gatherUpstreamContext()` 加智能截断策略 — 上游内容 >8000 字符用 AI 摘要化到 2000 字；或按集智能截取（只保留本集出场角色+相关场景）。
- **Prompt 质量不足**：`prompts.ts` 阶段 prompt 是简化版，缺少 drama-team 技能验证过的创作法则（每集必有冲突、Face-slap 必须直接暴力、分镜硬规则等）。需注入 phase-specific constraints。
- **Seedance 14 项检查未注入**：`prompt_optimization` prompt 缺少官方 14 项检查清单（中文、单人、分镜时序、情绪外化等），直接导致生视频质量差。

### 端口与启动

- 后端：`npx tsx server/index.ts` (端口 3000)
- 前端：`npx vite` (端口 5174)
- **重启前清理**：`pkill -f "tsx server/index.ts"`（旧进程残留导致 EADDRINUSE 崩溃）

### QA 验证结果 (Phase A-B)

| 阶段 | 耗时 | 内容量 | Aligner | 状态 |
|------|------|--------|---------|------|
| ip_analysis | ~2.5min | 1668 字 | 无 | ✅ |
| outline | ~2min | 1613 字 | 无 | ✅ |
| characters | ~3min | 2274 字 | 无 | ✅ |
| visual_assets | ~4min | 5560 字 | 无 | ✅ |
| script (EP-01) | ~4min | 3120 字 | 91/100 PASS (Round 1) | ✅ |
| storyboard (EP-01) | ~6.7min | 0 字 | — | ❌ 待修（上下文过长） |
| prompts (EP-01) | 未测试 | — | — | ⏳ |

### Phase C 制作层状态 (2026-05-10 盘点)

| 服务 | 代码状态 | 实机验证 | 备注 |
|------|---------|---------|------|
| image_gen (Dreamina) | 🟡 骨架完成 | ❌ 未验证 | CLI 调用+多账号切换+压缩 |
| video_gen (Seedance) | 🟡 骨架完成 | ❌ 未验证 | 4 张轻量参考+轮询下载 |
| assembly (FFmpeg) | 🟡 骨架完成 | ❌ 未验证 | 归一化+concat+降级方案 |

### 开发路线

- ✅ Phase A: 基础设施（前后端框架、API、WebSocket、基础布局）
- ✅ Phase B: 编剧层（IP→大纲→角色→视觉→剧本→分镜→Prompts + Aligner）
- ✅ **Phase C: 制作层**（prompt_optimization → Dreamina 生图 → Seedance 视频 → FFmpeg 合成）
- 🔵 Phase D: 高级功能（无限画布集成、AI 对话修改、小说上传、持久化存储）

---

## Phase C 制作层实现指南 (v2026-05-09 新增)

> Phase C 将编剧层的 Prompts 转化为最终成片：prompt 合规性检查 → Dreamina 生图 → Seedance 视频 → FFmpeg 合成。
> 项目位于 `~/.hermes/tasks/drama-studio/`，设计文档见 `references/drama-studio-design.md`。

### Phase C 架构

```
编剧输出 (prompts/EP-XX.md)
    ↓
prompt_optimization (14 项 Seedance 检查)
    ↓
Dreamina text2image (角色基础图 + 关键帧)
    ↓
Seedance multimodal2video (关键帧→视频片段，自带声音)
    ↓
FFmpeg 拼接 (成片输出)
```

### 1. prompt_optimization — Prompt 合规性检查 (9️⃣)

**为什么需要？** Seedance 2.0 有严格的 Prompt 格式要求，编剧层输出的英文 prompt 不能直接用于生视频。

**14 项检查清单（官方）：**

| # | 检查项 | 规则 |
|---|--------|------|
| 1 | 语言 | 必须是**中文**，不能英文 |
| 2 | 角色数 | **最多1个角色**（单人动作） |
| 3 | 场景 | 必须有，但**不做主体** |
| 4 | 动作 | 必须有，**角色核心内容**，**缓慢渐进** |
| 5 | 动作限制 | 避免快速移动、大幅旋转、激烈运动 |
| 6 | 禁止内容 | 不能含文字/字幕 |
| 7 | 视角 | **平视**，不能极端仰/俯 |
| 8 | 距离 | **近景或特写**，不能远景 |
| 9 | 角色特征 | 必须明确（年龄/性别/外貌/服装） |
| 10 | 角色一致性 | 同一角色外观不变 |
| 11 | 镜头运动 | 最多一种缓慢运动（推/拉/摇/移） |
| 12 | 时间描述 | **不能含时间点**（如"夜晚"→"灯光昏暗"） |
| 13 | 运镜术语 | **不能出现**"俯拍/推镜头/平移" |
| 14 | 字数 | 不超过 300 字 |

**Prompt 重写模板（✅ 通过所有检查）：**
```
{场景背景}。{角色描述}正在{缓慢动作}。{光影氛围}。
示例：古堡走廊烛火摇曳，石墙斑驳。一位苍白皮肤的年轻女子正缓缓抚摸胸口。她穿着黑色长裙，神情恐惧。昏暗的烛光映照出她紧张的面容。
```

**Prompt 优化 AI System Prompt 核心要素：**
- 逐条验证 14 项，不合格则重写
- 角色描述从上游 `characters.md` + `manifest.md` 提取（不自己编）
- 输出 JSON 格式：`{optimized: "...", fixes: [{id: N, original: "...", fixed: "..."}]}`

### 2. image_gen — Dreamina 生图 (🔟)

**不再按集生成！** 基础图全局复用：
- **角色基础图**：每个角色 1-2 张（正面肖像 + 侧面），用于后续关键帧参考
- **场景图**：每个唯一场景 1 张（无角色纯环境），用于 Seedance 场景参考
- **特写图**：关键道具/特效（如咬痕/发光）

**Dreamina 使用要点：**
- CLI 调用：`dreamina text2image --prompt "..." --aspect 9:16 --seed X`
- 多账号并行（`dreamina-multi-account` skill）
- 图片压缩 < 500KB 不稳定，建议 864x1536+ ~1MB
- 每账号同时仅 1 个任务

### 3. video_gen — Seedance 视频生成 (1️⃣1️⃣)

**关键帧引导法（核心工作流）：**
1. 先 text2image 生成 5-7 张关键图（60% → 90% prompt 强度）
2. 作为 `--image` 传入 multimodal2video
3. 每段 prompt 必须有人物动作/位置（否则空房间）

**Seedance 2.0 限制（⚠️ 避免翻车）：**
- 每段有且仅有 1 个角色（双人易融合/跳变）
- 动作缓慢渐进，忌大幅移动
- 场景做背景，"静止+微动作"
- 特效弱、黑屏/镜子做不好
- **原生生成带声音的视频**（无需额外配音）

### 4. assembly — FFmpeg 合成 (1️⃣2️⃣)

**拼接逻辑：**
```bash
# 将多个视频片段按顺序拼接
ffmpeg -f concat -i filelist.txt -c copy output.mp4
```

**filelist.txt 格式：**
```
file 'EP-01/shot-01.mp4'
file 'EP-01/shot-02.mp4'
...
```

**已知问题：**
- 种子账户 984268 无法使用 multimodal2video → 需切账号
- Prompt 优化是质量门控，不合格直接导致空视频
- 视频片段时长需与分镜时间对齐

### Phase C 后端实现要点

**services/pipeline.ts 新增方法：**
- `optimizePrompt()` — 调用 LLM 改写 prompt + 14 项验证
- `generateImage()` — Dreamina CLI 调用 + 图片路径记录
- `generateVideo()` — Seedance CLI 调用 + 结果验证
- `assembleEpisode()` — FFmpeg 拼接 + 成片输出

**数据模型扩展：**
```typescript
interface PhaseCData {
  optimized_prompts: string[];  // 优化后的中文 prompt
  image_paths: string[];         // Dreamina 输出图片路径
  video_paths: string[];         // Seedance 输出视频路径
  final_video: string;           // 成片路径
}
```

**常见陷阱：**
- 编剧 prompt 直接丢给 Seedance → 空视频/画面不符（必须经过优化）
- 角色基础图质量差 → 所有关键帧漂移（先验证角色图再批量）
- 账号同时多任务 → Dreamina 排队/失败（串行 or 多账号）
- Seedance 提示语含英文 → 直接失败（必须中文）

---

## GitHub 同步 (https://github.com/husw725/drama-team)

> 技能本地存储在 `~/.hermes/skills/creative/hermes-short-drama-team/`，通过 git remote 指向 `husw725/drama-team`。本地 skill 文件变化需要手动推送到 GitHub。

**同步流程：**
```bash
cd ~/.hermes/skills/creative/hermes-short-drama-team
# 1. 确保 remote 指向 drama-team 仓库
git remote set-url origin https://husw725:<TOKEN>@github.com/husw725/drama-team.git
# 2. 拉取远端（可能遇到 forced update）
git pull --rebase origin main
# 3. 添加新文件/变更
git add -A && git commit -m "feat: ..."
# 4. 推送
git push origin main
```

### 常见陷阱
- `git push` 被拒（remote 有新提交）→ `git pull --rebase origin main` 再 push
- rebase 可能导致本地独有文件丢失（如 `templates/fix_prompts_template.py` 曾丢失）→ 推送后检查文件完整性
- 本地 skill 文件 vs GitHub 仓库文件可能不同步 → 用 `git log --oneline` 对比确认

### vLLM 本地模型调用陷阱（⭐ 2026-05-13 验证）

> **问题**：Qwen3.6-27B-AWQ（带思考模式）通过 vLLM 调用时，返回 `reasoning` 字段而非 `content`，导致 `message.content` 为 `None`。

**根因**：模型的 reasoning 部分消耗了 max_tokens 预算，导致实际输出部分被截断或为空。

**修复方案**：
1. **max_tokens 必须足够大** — 至少 8192（含 reasoning 开销），而非 4096
2. **空值检查** — 调用后检查 `resp.choices[0].message.content` 是否为 `None`
3. **降级策略** — content 为 None 时重试或返回空

```python
# ❌ 错误：max_tokens 太小
resp = client.chat.completions.create(
    model="qwen27b-awq",
    messages=[...],
    max_tokens=4096  # reasoning 耗尽，content 为 None
)
return resp.choices[0].message.content  # TypeError: write() argument must be str, not None

# ✅ 正确：足够大的 max_tokens + None 检查
resp = client.chat.completions.create(
    model="qwen27b-awq",
    messages=[...],
    max_tokens=8192  # 给 reasoning 留足空间
)
content = resp.choices[0].message.content
if content is None:
    # 重试或返回空
    return ""
return content
```

**诊断命令**：
```bash
# 检查模型是否返回 reasoning
curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen27b-awq","messages":[{"role":"user","content":"hello"}],"max_tokens":20}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); m=d['choices'][0]['message']; print(f'content: {m.get(\"content\")}'); print(f'reasoning: {m.get(\"reasoning\")}')"
```

**批量生成分镜/Prompts 脚本模板**：
- 用 `openai` Python 库调用 vLLM（`base_url=http://localhost:8000/v1`）
- 好莱坞剧本解析：角色名全大写一行，对白下一行（无引号），parenthetical 行 `^\(.*\)$` 需跳过
- 脚本存为 `episodes_src/EP-NN.txt`（按 `EPISODE \d+:` 切分）
- 后台运行 + `notify_on_complete=true` 用于长时间任务（5-32集 × 每集约 2-5 分钟）

## 相关技能

- `hermes-agent` - Hermes Agent 基础使用
- `writing-plans` - 多步骤任务的规划方法
- `novel-to-short-drama-adaptation` - 小说改编短剧流程
- `short-drama-reviewer` - 多维度用户视角评审
- `short-dreamina-shot-generation` - 即梦CLI生图工作流
- `seedance2-short-drama-workflow` - Seedance 2.0 视频生成
- `drama-canvas-infinite-canvas` - 无限画布节点流水线系统（纯 DOM + CSS Transform，无线自动关联）⭐ **v2026-05-08 取代旧 React Flow 方案**
- `drama-project-index-page` (已归档至 `.archive/`，内容已合并到本技能的"生产工作台页面"章节)
