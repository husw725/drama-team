# 🎬 Drama Team v2.0 — 多 Agent 协作短剧编剧系统

<div align="center">

**从小说到成片的 AI 短剧全流程 — 含视觉资产一致性管控**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version: v2.0](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)]()
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)]()

📚 [文档](./docs/) | 📝 [快速开始](./docs/quickstart.md) | 📋 [实现指南](./docs/implementation.md) | 💡 [最佳实践](./docs/best-practices.md)

</div>

---

## 🌟 为什么需要 Drama Team？

传统 AI 短剧创作面临四大挑战：

| 问题 | 传统方案 | Drama Team v2.0 方案 |
|------|---------|---------------------|
| **节奏拖沓** | 一次性生成，缺乏控制 | 六阶段创作，每集严格审核 |
| **爽点稀疏** | AI 不懂短剧商业逻辑 | 内置 Aligner v4.0 审核标准 |
| **质量不稳** | 没有质量检查机制 | 独立 Script Aligner 严格把关 |
| **视觉不一致** | AI 生图时角色外观漂移 | **⭐ 视觉资产清单 + Prompt 强制注入** |

**Drama Team v2.0** 通过 **多 Agent 协作**、**质量门禁** 和 **视觉资产管控** 机制，全面解决这些问题：

- ✅ **专业分工**：Writer 创作、Aligner 审核、Recorder 记录、**Visual Director 管外观**
- ✅ **六阶段流程**：大纲 → 人物 → **视觉资产清单** → 剧本 → 分镜 → AI Prompts
- ✅ **视觉一致性**：manifest.md 作为视觉单一真相源，Prompts 强制注入
- ✅ **文档驱动**：所有内容持久化，支持断点续写

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/husw725/drama-team.git
cd drama-team

# 2. 创建新项目
mkdir my-drama && cd my-drama
cp ../templates/*.md .
mkdir visual_assets script storyboard prompts

# 3. 填写项目信息
nano outline.md          # 大纲
nano character.md        # 人物
nano visual_assets/manifest.md  # 视觉资产清单 ⭐ v2.0 新增

# 4. 开始创作（配合 Hermes Agent 使用）
# 使用 delegate_task 派编剧 + Aligner 审核
```

## 🎯 核心功能

### 1️⃣ 六阶段创作流程（v2.0）

```
┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌────────┐  ┌──────────┐  ┌────────────┐
│ 1.大纲   │→ │ 2.人物   │→ │ 3.视觉资产   │→ │ 4.剧本 │→ │ 5.分镜   │→ │ 6.Prompts  │
│ 故事方向 │  │ 性格关系 │  │ 外观规范 ⭐ │  │ 剧情对白 │  │ 镜头设计 │  │ AI生图指令 │
└──────────┘  └──────────┘  └──────────────┘  └────────┘  └──────────┘  └────────────┘
```

**v2.0 关键新增：第3阶段「视觉资产清单」** — 定义角色外观、服装、道具、场景的视觉规范，后续所有 AI Prompts 强制从此清单注入。

### 2️⃣ 多 Agent 协作架构

```
┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  主编剧      │→ │ 视觉导演     │→ │ Script      │→ │ Script      │→ │ 编剧/审核   │
│  (Writer)   │  │ (Visual Dir) │  │ Aligner v4  │  │ Recorder    │  │ 独立审核    │
└─────────────┘  └──────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
                     │                  │                      │              │
                     │            (PASS/FAIL)           (进度记录)       (独立验证)
                     │                  │                      │              │
                     └──────────────────┼──────────────────────┘              │
                                (视觉资产清单)                               │
                                                                            │
                         Prompts 强制注入 ←─────────────────────────────────┘
```

**四个核心 Agent**：
- **👨‍💼 Writer（主编剧）**：创作剧本、分镜、AI Prompts
- **🎨 Visual Director（视觉导演）**：创建视觉资产清单，定义角色外观、服装、道具、场景
- **🔍 Aligner v4.0（审核员）**：10 维审核（含视觉一致性），独立评分
- **📝 Recorder（记录员）**：维护项目记忆，追踪进度和伏笔

### 3️⃣ 视觉一致性系统（⭐ v2.0 核心特性）

**问题**：AI 生图时，同一角色在不同集的瞳色、服装、发型经常漂移。

**v2.0 解决方案**（三重保障）：

| 机制 | 说明 |
|------|------|
| **视觉资产清单** | `manifest.md` 定义每个角色的精确外观（瞳色、发色、服装、道具、场景） |
| **Prompt 强制注入** | 每张图 Prompt 开头逐字复制 manifest.md 中的角色描述 |
| **审核员一致性检查** | Aligner v4.0 对比 Prompts 与 manifest.md，不一致即扣分 |

### 4️⃣ 短剧创作法则（内置）

- ⚡ **节奏控制**：每集必有冲突，3 秒没冲突就划走
- 💬 **对话简洁**：每句≤15 字，快速有力
- 🔥 **情感爆炸**：Face-slap 必须直接暴力
- 🎣 **悬念明确**：Cliffhanger 必须具体
- 👁️ **视觉记忆点**：每集至少 1 个标志性视觉镜头

### 5️⃣ 项目目录结构

```
project/
├── TASK.md                      # 任务进度跟踪
├── outline.md                   # 故事大纲
├── characters/
│   └── characters.md            # 人物设定
├── visual_assets/
│   ├── manifest.md              # 视觉资产清单 ⭐
│   └── references/              # 参考图
├── script/
│   └── EP-XX.md                 # 各集剧本
├── storyboard/
│   └── EP-XX.md                 # 各集分镜
├── prompts/
│   └── EP-XX.md                 # 各集 AI Prompts
└── script.progress.md           # 创作进度
```

## 📊 审核标准（Aligner v4.0）

| 维度 | 权重 | 说明 |
|------|------|------|
| 开局钩子 | 15% | 前3秒必须有视觉冲击/冲突爆发 |
| 冲突强度 | 20% | 每集冲突绑定不可逆代价 |
| 悬念钩子 | 15% | 结尾必须"不看不行" |
| 倒计时/紧迫感 | 10% | 全剧有明确期限 |
| 人物弧光 | 10% | 主角有成长线 |
| 核心关系 | 10% | 体现核心关系卖点 |
| 信息揭露节奏 | 10% | 暗示→部分揭露→实锤 |
| 重复剧情 | 5% | 同模式连续≥2集预警 |
| 视觉记忆点 | 5% | 每集至少1个标志性镜头 |
| **视觉一致性** ⭐ | **5%** | **Prompts 与 manifest.md 一致** |

**≥80 分 → PASS | 70-79 分 → ⚠️ 需修改 | ≤70 分 → FAIL**

## 🛠️ 技术栈

- **核心**: Hermes Agent + delegate_task
- **架构**: 多 Agent 协作 + 独立审核
- **存储**: 文档驱动（Markdown）
- **审核**: Aligner v4.0（10维评分）
- **视觉**: manifest.md 单一真相源

## 📚 文档导航

| 文档 | 描述 |
|------|------|
| [快速开始](./docs/quickstart.md) | 5 分钟搭建系统 |
| [实现指南](./docs/implementation.md) | 详细实现步骤 |
| [最佳实践](./docs/best-practices.md) | 避免常见错误 |
| [Agent 提示词](./prompts/) | 各 Agent 详细定义 |
| [Hermes Skill](./SKILL.md) | 完整的 Hermes Agent 技能文件 |

## ⚠️ 注意事项

- **AI 审核有局限** — Aligner 本身是 AI，必须人工最终把关
- **视觉资产清单是单一真相源** — 任何外观修改要同步更新 manifest.md
- **FAIL 成本** — 同一问题 FAIL 超过 2-3 次立即人工介入

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

**🎬 让 AI 成为你的编剧助手，而不是替代品**

*AI 产出 60 分骨架，人工提升到 80 分精品*

</div>
