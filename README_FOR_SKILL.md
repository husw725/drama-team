# Drama Team Skill - 使用说明

## 🎯 这个 Skill 能做什么？

这个 skill 让 OpenClaw 具备**短剧剧本创作能力**，通过多 Agent 协作自动完成：

1. ✅ 剧本创作（Writer Agent）
2. ✅ 质量审核（Aligner Agent）
3. ✅ 进度追踪（Recorder Agent）
4. ✅ 迭代优化（自动修改直到通过）

---

## 🚀 如何使用

### 方式 1: 直接告诉 OpenClaw

```
你：帮我创作一部悬疑短剧
```

OpenClaw 会自动：
- 创建项目结构
- 启动 Writer Agent 创作
- 启动 Aligner Agent 审核
- 迭代优化直到通过
- 记录进度

### 方式 2: 使用脚本

```bash
# 创建项目
mkdir my-drama && cd my-drama
cp ../skills/drama-team/templates/*.md .

# 填写信息
nano outline.md character.md episode-index.md

# 运行
node ../skills/drama-team/scripts/drama_team.js . 1
```

### 方式 3: 手动调用 Agent

在 OpenClaw 中：

```javascript
// 启动 Writer
sessions_spawn({
  runtime: "acp",
  agentId: "drama-writer",
  task: "创作 EP-01 剧本",
  cwd: "/path/to/project"
})
```

---

## 📋 完整工作流程

```
用户请求
   ↓
创建项目结构
   ↓
启动 Writer Agent ────→ 创作剧本
   ↓
启动 Aligner Agent ────→ 审核质量
   ↓
   ├─ PASS → 继续
   └─ FAIL → 返回 Writer 修改
             ↓
          重新审核
             ↓
          (最多 5 次)
   ↓
启动 Recorder Agent ────→ 记录进度
   ↓
完成 ✅
```

---

## 🎬 实际示例

### 创建悬疑短剧

```
用户：帮我创作一部悬疑短剧

助手：
好的！创建项目《午夜来电》...

[创建结构]
[填写大纲、人物、集目录]

开始创作 EP-01...

[Writer Agent] 创作中...
[Writer Agent] 完成

[Aligner Agent] 审核中...
[Aligner Agent] FAIL: 开场无冲突

[Writer Agent] 根据反馈修改...
[Writer Agent] 完成

[Aligner Agent] 审核中...
[Aligner Agent] PASS ✅

[Recorder Agent] 记录进度...

✅ EP-01 创作完成！
- 质量评分: 4.8/5.0
- 迭代次数: 2
- 文件: EP-01.md
```

---

## 📁 项目结构

创作完成后，项目目录：

```
my-drama/
├── outline.md           # 大纲
├── character.md         # 人物设定
├── episode-index.md     # 24集规划
├── EP-01.md            # 第一集 ✅
├── EP-02.md            # 第二集（待创作）
└── script.progress.md   # 进度记录
```

---

## ⚙️ Agent 说明

### Writer Agent
- **职责**: 创作剧本
- **输入**: 大纲、人物、集目录
- **输出**: EP-XX.md
- **遵循**: 短剧创作法则

### Aligner Agent
- **职责**: 审核质量
- **输入**: EP-XX.md
- **输出**: PASS/FAIL + 反馈
- **标准**: 7 条审核标准

### Recorder Agent
- **职责**: 记录进度
- **输入**: 剧本 + 审核结果
- **输出**: 更新 script.progress.md
- **追踪**: 伏笔、决策、历史

---

## 📊 质量标准

Aligner Agent 会检查：

1. ✅ 每集有明确冲突
2. ✅ 节奏紧凑
3. ✅ 对话≤15字
4. ✅ Face-slap 直接暴力
5. ✅ 情感表达爆炸式
6. ✅ Cliffhanger 明确
7. ✅ 危机-救援结构

---

## 💡 最佳实践

1. **成本控制**: 设置合理的迭代上限（3-5次）
2. **人工把关**: AI 审核可能僵化，最终需人工确认
3. **及时介入**: 反复 FAIL 时人工介入
4. **断点续写**: 随时暂停，随时恢复

---

## 🔧 配置要求

要使用这个 skill，需要：

1. ✅ OpenClaw 已安装
2. ✅ 支持 sessions_spawn（启动 Agent）
3. ✅ 支持文件读写

---

## 📚 文档

- `SKILL.md` - 完整使用指南
- `AGENTS.yaml` - Agent 配置
- `docs/quickstart.md` - 快速开始
- `docs/implementation.md` - 实现细节
- `examples/sample-project/` - 完整示例

---

**版本**: 2.0
**状态**: ✅ 可用
**更新**: 2026-04-22
