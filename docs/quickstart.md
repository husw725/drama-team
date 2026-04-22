# 快速开始 - 5 分钟搭建多 Agent 协作系统

## 目标
在 5 分钟内搭建一个可运行的短剧编剧多 Agent 协作系统。

## 前置条件
1. OpenClaw 已安装并运行
2. 支持任务委派（类似 `delegate_task` 工具）
3. 支持文件读写操作

## 步骤 1: 克隆学习资料包 (30 秒)

```bash
# 方式 1: 从 GitHub 克隆（如果已发布）
git clone <repo-url> openclaw-drama-team-learning
cd openclaw-drama-team-learning

# 方式 2: 下载解压
# 下载压缩包并解压到工作目录
```

## 步骤 2: 创建项目目录 (30 秒)

```bash
# 创建新项目目录
mkdir my-drama-project
cd my-drama-project

# 复制模板文件
cp ../openclaw-drama-team-learning/templates/*.md .
```

## 步骤 3: 填写项目信息 (2 分钟)

### 3.1 编辑 outline.md

```bash
nano outline.md
```

填写关键信息：
- 题材：复仇/甜宠/悬疑
- 结局类型：HE/BE/OE
- 核心爽点：打脸/逆袭/复仇
- 故事梗概：200 字以内

### 3.2 编辑 character.md

填写主要人物：
- 女主姓名、年龄、职业、核心特质
- 男主姓名、年龄、职业、核心特质
- 反派姓名、与主角关系、核心动机

### 3.3 编辑 episode-index.md

规划集目录：
- 每集的标题
- 每集的核心冲突
- 每集的爽点设计

## 步骤 4: 配置 Agent (1 分钟)

### 4.1 确认提示词已就绪

```bash
# 检查提示词文件
ls ../openclaw-drama-team-learning/prompts/
# 应该看到：writer.md, aligner.md, recorder.md
```

### 4.2 根据 OpenClaw 调整脚本

编辑 `drama_team.py`，将 TODO 部分替换为 OpenClaw 的实际工具调用：

```python
# 原代码:
# TODO: 使用 OpenClaw 的任务委派工具
# result = delegate_task(...)

# 替换为:
result = openclaw_delegate_task(
    goal=goal,
    context=full_context,
    toolsets=['file']
)
```

## 步骤 5: 开始创作 (1 分钟)

```bash
# 运行主脚本
python ../openclaw-drama-team-learning/scripts/drama_team.py
```

### 预期输出

```
============================================================
短剧编剧团队 - 多 Agent 协作系统
============================================================

开始创作 EP-01...

==================================================
EP-01 - 第 1 次迭代
==================================================

[1/3] 主编剧正在创作...
[2/3] Script Aligner 正在审核...
[3/3] ❌ 审核未通过
反馈：开场无冲突，需要增加直接动作...

⏭️  继续第 2 次迭代...

==================================================
EP-01 - 第 2 次迭代
==================================================
...
```

## 下一步

### 深入学习
1. 阅读 [README.md](../README.md) 了解核心概念
2. 查看 [实现指南](docs/implementation.md) 了解详细实现
3. 学习 [最佳实践](docs/best-practices.md) 避免常见错误

### 参考示例
查看 [示例项目](examples/sample-project/) 了解完整的项目结构：
- `outline.md`: 完整的大纲示例
- `EP-01.md`: 通过审核的剧本示例
- `script.progress.md`: 进度记录示例

### 自定义配置
- 调整 [Agent 提示词](prompts/) 以适应不同题材
- 修改 [文档模板](templates/) 以符合个人风格
- 扩展 [核心脚本](scripts/drama_team.py) 添加新功能

## 常见问题

### Q: 如何调整审核标准？
A: 编辑 `prompts/aligner.md`，修改审核标准部分。

### Q: 如何增加新的 Agent？
A: 参考现有 Agent 的提示词格式，创建新的提示词文件，并在脚本中添加对应的委派函数。

### Q: 如何控制成本？
A: 调整 `max_iterations` 参数，设置合适的最大迭代次数（建议 3-5 次）。

### Q: 如何暂停和恢复？
A: 系统基于文档驱动，随时可以暂停。恢复时从 `script.progress.md` 读取进度继续。

## 故障排查

### 问题 1: Agent 无法创建
**原因**: OpenClaw 不支持任务委派工具  
**解决**: 检查 OpenClaw 文档，确认正确的工具名称和用法

### 问题 2: 审核总是 FAIL
**原因**: 审核标准过于严格或 Writer 提示词不清晰  
**解决**: 放宽审核标准或改进 Writer 提示词

### 问题 3: 迭代次数过多
**原因**: 同一问题反复出现  
**解决**: 检查是否是规则问题，必要时人工介入

## 获取帮助

- 查看 [最佳实践](docs/best-practices.md) 中的"常见陷阱与避免方法"
- 参考 [示例项目](examples/sample-project/) 的完整案例
- 联系项目维护者或社区

---

**预计时间**: 5 分钟  
**难度**: ⭐⭐☆☆☆  
**先决条件**: OpenClaw 基础使用
