# 🎬 Drama Team - 多 Agent 协作短剧编剧系统

<div align="center">

**使用多 Agent 协作架构，打造符合商业逻辑的高质量短剧剧本**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)]()

📚 [文档](./docs/) | 📝 [快速开始](./docs/quickstart.md) | 📋 [实现指南](./docs/implementation.md) | 💡 [最佳实践](./docs/best-practices.md)

</div>

---

## 🌟 为什么需要 Drama Team？

传统 AI 剧本创作面临三大挑战：

| 问题 | 传统方案 | Drama Team 方案 |
|------|---------|---------------|
| **节奏拖沓** | 一次性生成，缺乏控制 | 分阶段创作，每集严格审核 |
| **爽点稀疏** | AI 不懂短剧商业逻辑 | 内置短剧创作法则，强制爽点分布 |
| **质量不稳** | 没有质量检查机制 | Script Aligner 严格把关，不通过不继续 |

**Drama Team** 通过 **多 Agent 协作** 和 **质量门禁** 机制，解决这些问题：

- ✅ **专业分工**：Writer 创作、Aligner 审核、Recorder 记录
- ✅ **质量门禁**：必须通过审核才能进入下一阶段
- ✅ **文档驱动**：所有内容持久化，支持断点续写
- ✅ **成本可控**：迭代次数限制，避免无限循环

## 🚀 快速开始

### 5 分钟上手

```bash
# 1. 克隆项目
git clone https://github.com/husw725/drama-team.git
cd drama-team

# 2. 创建新项目
mkdir my-drama && cd my-drama
cp ../templates/*.md .

# 3. 填写项目信息（大纲、人物、集目录）
nano outline.md
nano character.md
nano episode-index.md

# 4. 开始创作
python ../scripts/drama_team.py
```

详细步骤请查看 [快速开始指南](./docs/quickstart.md)

## 🎯 核心功能

### 1️⃣ 多 Agent 协作架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   主编剧     │ ──→ │  Script      │ ──→ │  Script      │
│   (Writer)  │     │  Aligner     │     │  Recorder    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                  │                    │
       │              (审核结果)               │
       │                  │                    │
       └─────── FAIL ────┘                    │
                 (修改建议)                   │
                                             (记录)
```

**三个核心 Agent**：
- **👨‍💼 Writer（主编剧）**：负责创作剧本，遵循短剧法则
- **🔍 Aligner（审核员）**：严格审核质量，返回 PASS/FAIL
- **📝 Recorder（记录员）**：维护项目记忆，追踪进度和伏笔

### 2️⃣ 短剧创作法则（内置）

系统内置短剧行业核心法则，确保剧本符合商业逻辑：

- ⚡ **节奏控制**：每集必有冲突，3 秒没冲突就划走
- 💬 **对话简洁**：每句≤15 字，快速有力
- 🔥 **情感爆炸**：Face-slap 必须直接暴力（泼红酒、推搡）
- 🎣 **悬念明确**：Cliffhanger 必须具体（"Montana 见，我的真爱等你"）
- 💰 **付费点设计**：第 20 集必须设置足够吸引人的付费点

### 3️⃣ 文档驱动架构

```
project/
├── outline.md           # 大纲（题材、人物、爽点分布）
├── character.md         # 人物设定（性格、弧光、台词风格）
├── episode_index.md     # 集目录（每集标题、冲突、爽点）
├── script.progress.md   # 进度记录（决策、修改历史、伏笔）
└── EP-XX.md            # 各集剧本（通过审核后保存）
```

## 📖 使用示例

### 创建第一集剧本

```python
from scripts.drama_team import DramaTeam

# 初始化项目
team = DramaTeam('my-drama-project')

# 准备上下文
context = {
    'outline': '复仇题材，女主被背叛后华丽转身',
    'characters': '女主：坚强独立；男主：霸道总裁',
    'episode_plan': 'EP-01: 女主回国，时尚周亮相'
}

# 创建剧本（自动迭代直到通过审核）
team.create_episode(1, context, max_iterations=5)
```

### 典型创作流程

```
EP-01 创作过程:
├─ 第 1 次迭代：开场无冲突 ❌
│  └─ 修改：增加直升机颠簸 + 尖叫
├─ 第 2 次迭代：情感温和 ❌
│  └─ 修改："对不起" → "我要你生不如死"
└─ 第 3 次迭代：通过审核 ✅
   └─ 保存：EP-01.md
```

## 📊 项目统计

- **平均迭代次数**: 3 次（EP-01 通常需要 3 次建立模式）
- **审核通过率**: 第 3 次通过率 > 90%
- **创作速度**: 单集约 5-10 分钟（取决于复杂度）
- **成本优化**: 模式建立后，EP-03 后通常 2-3 次即可通过

## 🛠️ 技术栈

- **核心**: Python 3.8+
- **架构**: 多 Agent 协作（delegate_task）
- **存储**: 文档驱动（Markdown）
- **审核**: 规则引擎 + AI 判断

## 📚 文档导航

| 文档 | 描述 | 适合人群 |
|------|------|---------|
| [快速开始](./docs/quickstart.md) | 5 分钟搭建系统 | 新手 |
| [实现指南](./docs/implementation.md) | 详细实现步骤 | 开发者 |
| [最佳实践](./docs/best-practices.md) | 避免常见错误 | 进阶用户 |
| [Agent 提示词](./prompts/) | 各 Agent 详细定义 | 定制开发者 |

## 🌈 特色功能

### 🎭 分阶段创作

```
大纲 → 人物 → 集目录 → 剧本正文
  ↓      ↓       ↓          ↓
必须通过审核才能进入下一阶段
```

### 🔒 质量门禁

- 每集必须通过 Aligner 审核
- 审核不通过返回具体修改建议
- 循环迭代直到通过（最多 5 次）

### 📈 进度追踪

- 实时计算创作进度百分比
- 自动记录所有创作决策
- 伏笔埋设与回收追踪

### 🔄 断点续写

- 基于文档驱动，随时可以暂停
- 清空对话也能继续创作
- 进度记录完整可追溯

## ⚠️ 注意事项

### AI 审核的局限性

- Aligner 本身是 AI，可能僵化执行规则
- 可能对"格式正确但创意平庸"的剧本给 PASS
- **必须人工最终把关**

### 成本控制

- FAIL → 修改 → 再 FAIL 可能消耗大量 Token
- 同一问题反复 FAIL 超过 2-3 次时立即人工介入
- 要么修改规则，要么手动编辑剧本

### 记忆污染风险

- 手动修改文档会导致 Recorder 记录过时
- **修改文档后需要手动更新 `script.progress.md`**

## 🤝 贡献指南

欢迎贡献！以下是参与方式：

1. 🐛 **报告 Bug**: 提交 Issue
2. 💡 **功能建议**: 提交 Issue 或 Discussion
3. 🔧 **修复问题**: 提交 Pull Request
4. 📝 **改进文档**: 任何文档改进都受欢迎

## 📄 许可证

[MIT License](LICENSE)

## 🙏 致谢

- 感谢所有短剧创作者提供的行业洞察
- 基于 Hermes Agent 的多 Agent 协作理念
- 参考了多个成功短剧作品的创作模式

## 📧 联系方式

- **GitHub Issues**: [报告问题](https://github.com/husw725/drama-team/issues)
- **Email**: husw725@example.com

---

<div align="center">

**🎬 让 AI 成为你的编剧助手，而不是替代品**

*AI 产出 60 分骨架，人工提升到 80 分精品*

[![Star History](https://api.star-history.com/svg?repos=husw725/drama-team&type=Date)](https://star-history.com/#husw725/drama-team&Date)

</div>
