# 快速开始 - Drama Team v2.0

## 目标

在 5 分钟内搭建一个可运行的短剧编剧多 Agent 协作系统。

## 前置条件

1. Hermes Agent 已安装并运行
2. 支持 `delegate_task` 工具
3. 支持文件读写操作

## 步骤 1: 克隆项目 (30秒)

```bash
git clone https://github.com/husw725/drama-team.git
cd drama-team
```

## 步骤 2: 创建项目目录 (30秒)

```bash
mkdir my-drama && cd my-drama

# 复制模板
cp ../templates/outline.md .
cp ../templates/character.md .
cp ../templates/episode-index.md .
cp ../templates/episode.md .

# 创建目录结构
mkdir visual_assets script storyboard prompts

# 复制视觉资产模板
cp ../templates/visual-asset-manifest.md visual_assets/manifest.md
```

## 步骤 3: 填写项目信息 (2分钟)

### 3.1 编辑 outline.md
- 题材：复仇/甜宠/悬疑
- 结局类型：HE/BE/OE
- 核心爽点：打脸/逆袭/复仇
- 故事梗概：200字以内

### 3.2 编辑 character.md
- 女主/男主/反派姓名、年龄、职业、核心特质
- 人物关系、核心动机

### 3.3 编辑 visual_assets/manifest.md ⭐ v2.0 新增
- 角色外观（瞳色、发色、肤色、体态）
- 服装（按场景分类）
- 场景视觉（风格、色调、光源）
- 道具清单

**重要**：视觉资产清单必须经导演（用户）确认后才能进入剧本阶段。

## 步骤 4: 配置 Agent (1分钟)

检查提示词文件：
```bash
ls ../prompts/
# 应该看到：writer.md, aligner.md, recorder.md
```

## 步骤 5: 开始创作 (配合 Hermes Agent)

### 工作流

```
大纲 → 人物 → 视觉资产清单 → 剧本 → 分镜 → AI Prompts
                                              ↓
                                       Aligner v4.0 审核
                                              ↓
                                      PASS ✅ → 下一集
                                      FAIL ❌ → 修改重审
```

### 使用 Hermes Agent delegate_task

```python
# 派编剧写 EP-01
result = delegate_task(
    goal="创作 EP-01 三件套（剧本+分镜+Prompts）",
    context="""
    你是短剧主编剧。
    大纲：[outline.md 内容]
    人物：[characters.md 内容]
    视觉资产清单：[manifest.md 内容]
    要求：每张图 Prompt 逐字复制角色外观描述自 manifest.md
    """,
    toolsets=['file']
)

# 派独立审核员审核
result = delegate_task(
    goal="审核 EP-01 三件套是否符合 Aligner v4.0 标准",
    context="""
    你是 Script Aligner 审核员。
    审核标准：Aligner v4.0（10项评分，含视觉一致性）
    剧本内容：[EP-01 剧本完整内容]
    分镜内容：[EP-01 分镜完整内容]
    Prompts内容：[EP-01 Prompts完整内容]
    视觉资产清单：[manifest.md 完整内容]
    """,
    toolsets=['file']
)
```

## 下一步

### 深入学习
1. 阅读 [README.md](../README.md) 了解核心概念
2. 查看 [实现指南](implementation.md) 了解详细实现
3. 学习 [最佳实践](best-practices.md) 避免常见错误
4. 加载 [SKILL.md](../SKILL.md) 获取完整 Hermes Agent 技能

### v2.0 新增特性
- **视觉资产清单**：定义角色外观、服装、道具的统一规范
- **Prompt 强制注入**：每张图 Prompt 开头必须包含角色外观描述
- **Aligner v4.0**：新增视觉一致性检查维度
- **六阶段流程**：大纲→人物→视觉资产→剧本→分镜→Prompts

## 常见问题

### Q: 如何调整审核标准？
A: 编辑 `prompts/aligner.md`，修改审核标准部分。

### Q: 如何确保角色外观一致？
A: 填写 `visual_assets/manifest.md`，编剧写 Prompts 时逐字复制清单中的描述。

### Q: 如何控制成本？
A: 同一集 FAIL 超过 2-3 次立即人工介入。

---

**预计时间**: 5分钟
**难度**: ⭐⭐☆☆☆
**v2.0 新增**: 视觉资产清单阶段
