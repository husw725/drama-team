# 实现指南 - 在 OpenClaw 中实现多 Agent 协作系统

## 前置条件

1. OpenClaw 支持任务委派（类似 `delegate_task` 工具）
2. 支持文件读写操作
3. 支持多会话/多上下文管理

## 第一步：创建项目结构

```bash
mkdir -p drama-project/{docs,prompts,templates,scripts}
cd drama-project
```

## 第二步：定义 Agent 提示词

### 2.1 主编剧 (Writer) 提示词

```
# 角色：短剧主编剧

## 职责
- 负责创作剧本初稿
- 遵循短剧创作法则和模板
- 根据 Aligner 的反馈进行修改

## 创作法则
- 每集必有冲突
- 节奏紧凑（3 秒没冲突就划走）
- 对话≤15 字
- 爽点分布合理
- 第 20 集必须设置付费点

## 输出要求
- 遵循剧本模板格式
- 场景描述简洁
- 对话简短有力
- 情感表达爆炸式
```

### 2.2 Script Aligner 提示词

```
# 角色：剧本质量检查员

## 职责
- 审核剧本是否符合短剧标准
- 返回 PASS 或 FAIL
- 提供具体的修改建议

## 审核标准

### 必须通过（否则 FAIL）
1. 每集有明确的冲突
2. 节奏紧凑，无冗余描写
3. 对话简短（≤15 字）
4. 情感表达强烈

### Face-slap 必须直接暴力
- ✅ 有效：泼红酒、推搡、抢物品、肢体冲突
- ❌ 无效：口头嘲讽、眼神不屑、翻白眼

### 情感表达必须爆炸式
- ✅ 有效："我要你生不如死！"、"你是我的！"
- ❌ 无效："对不起"、"谢谢你"、"是你..."

### Cliffhanger 必须明确
- ✅ 有效："Montana 见，我的真爱在那里等你"
- ❌ 无效："她不知道，这次旅行将改变她的一生..."

## 返回格式

### 通过时
```
PASS
```

### 不通过时
```
FAIL

修改建议：
1. [具体问题 1]
2. [具体问题 2]
3. [具体问题 3]

参考模式：
- [类似场景的正确写法]
```
```

### 2.3 Script Recorder 提示词

```
# 角色：创作进度记录员

## 职责
- 维护项目记忆和创作历史
- 记录创作决策
- 追踪伏笔埋设与回收
- 计算进度百分比

## 记录内容

### 创作决策
- 故事方向选择
- 人物设定决策
- 情节走向选择
- 修改原因

### 伏笔追踪
- [伏笔名称] - [埋设位置] - [回收位置] - [状态：待回收/已回收]

### 进度计算
- 总集数：X
- 已完成：Y
- 进度：Y/X * 100%

## 更新时机
- 每个阶段完成后
- 每次重要决策后
- 每次 Aligner 审核通过后
```

## 第三步：创建核心脚本

### 3.1 主控制脚本 (drama_team.py)

```python
#!/usr/bin/env python3
"""
短剧编剧团队 - 主控制脚本
使用多 Agent 协作方式创作短剧剧本
"""

import os
from pathlib import Path

# Agent 提示词
WRITER_PROMPT = """
[从 prompts/writer.md 读取]
"""

ALIGNER_PROMPT = """
[从 prompts/aligner.md 读取]
"""

RECORDER_PROMPT = """
[从 prompts/recorder.md 读取]
"""

class DramaTeam:
    def __init__(self, project_dir):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(exist_ok=True)
        
    def create_episode(self, episode_num, context):
        """
        创建单集剧本
        
        Args:
            episode_num: 集数
            context: 上下文信息（大纲、人物、集目录等）
        """
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # 1. 主编剧创作
            script = self.delegate_to_writer(
                goal=f"创作 EP-{episode_num:02d} 剧本",
                context=context,
                iteration=iteration
            )
            
            # 2. Script Aligner 审核
            result = self.delegate_to_aligner(
                goal=f"审核 EP-{episode_num:02d} 剧本",
                script=script
            )
            
            # 3. 检查审核结果
            if result['status'] == 'PASS':
                # 4. Script Recorder 记录
                self.delegate_to_recorder(
                    goal=f"记录 EP-{episode_num:02d} 创作完成",
                    episode_num=episode_num,
                    context=context
                )
                
                # 5. 保存剧本
                self.save_script(episode_num, script)
                return True
            else:
                # 6. 返回修改，进入下一轮迭代
                context['feedback'] = result['feedback']
                print(f"第 {iteration} 次审核未通过，正在修改...")
        
        # 超过最大迭代次数，需要人工介入
        print(f"警告：EP-{episode_num:02d} 超过最大迭代次数，需要人工介入")
        return False
    
    def delegate_to_writer(self, goal, context, iteration=1):
        """委派任务给主编剧 Agent"""
        # 使用 OpenClaw 的任务委派工具
        # 伪代码，根据实际工具调整
        result = delegate_task(
            goal=goal,
            context=f"""
{WRITER_PROMPT}

当前上下文：
{context}

迭代次数：{iteration}
{'上轮反馈：' + context.get('feedback', '') if iteration > 1 else ''}
            """,
            toolsets=['file']
        )
        return result.output
    
    def delegate_to_aligner(self, goal, script):
        """委派任务给 Script Aligner Agent"""
        result = delegate_task(
            goal=goal,
            context=f"""
{ALIGNER_PROMPT}

待审核剧本：
{script}
            """,
            toolsets=['file']
        )
        
        # 解析审核结果
        output = result.output
        if output.startswith('PASS'):
            return {'status': 'PASS'}
        else:
            return {
                'status': 'FAIL',
                'feedback': output.replace('FAIL\n\n', '')
            }
    
    def delegate_to_recorder(self, goal, episode_num, context):
        """委派任务给 Script Recorder Agent"""
        delegate_task(
            goal=goal,
            context=f"""
{RECORDER_PROMPT}

当前进度：
- 集数：EP-{episode_num:02d}
- 项目信息：{context}

请更新 script.progress.md 文件
            """,
            toolsets=['file']
        )
    
    def save_script(self, episode_num, script):
        """保存剧本到文件"""
        filename = f"EP-{episode_num:02d}.md"
        path = self.project_dir / filename
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"剧本已保存：{path}")


# 使用示例
if __name__ == '__main__':
    team = DramaTeam('my-drama-project')
    
    # 创建第一集
    context = {
        'outline': '复仇题材，女主被背叛后华丽转身',
        'characters': '女主：坚强独立；男主：霸道总裁',
        'episode_plan': 'EP-01: 女主被背叛，发现真相'
    }
    
    team.create_episode(1, context)
```

## 第四步：创建文档模板

### 4.1 大纲模板 (templates/outline.md)

```markdown
# 短剧大纲

## 基本信息
- **题材**: [复仇/甜宠/悬疑/其他]
- **结局类型**: [HE/BE/OE]
- **核心爽点**: [打脸/逆袭/复仇/其他]

## 故事梗概
[200 字以内的故事概述]

## 主要人物
- **女主**: [姓名] - [核心特质]
- **男主**: [姓名] - [核心特质]
- **反派**: [姓名] - [核心特质]

## 核心冲突
[故事的主要矛盾]

## 爽点分布
- **EP-01~05**: [前期爽点]
- **EP-06~15**: [中期爽点]
- **EP-16~20**: [后期爽点 + 付费点]
```

### 4.2 剧本模板 (templates/episode.md)

```markdown
# EP-XX [集标题]

## 场景 1: [场景名称]
**时间**: [日/夜]
**地点**: [具体地点]

[场景描述，简洁明了]

**人物**: [出场人物]

[动作描述]

**[人物 A]**: [对话，≤15 字]

**[人物 B]**: [对话，≤15 字]

---

## 场景 2: [场景名称]
...

---

## 本集亮点
- [核心冲突]
- [爽点设计]
- [悬念设置]
```

## 第五步：运行和测试

```bash
# 1. 设置项目目录
mkdir my-drama
cd my-drama

# 2. 复制模板文件
cp ~/openclaw-drama-team-learning/templates/*.md .

# 3. 运行主脚本
python drama_team.py
```

## 常见问题

### Q: Agent 之间如何传递信息？
A: 通过文档和 context 参数传递。每个 Agent 可以读写项目文档。

### Q: 如何控制成本？
A: 设置最大迭代次数，超过后人工介入。

### Q: 如何保证质量？
A: Aligner 严格审核 + 人工最终把关。

### Q: 如何避免记忆污染？
A: 手动修改文档后，需要更新 script.progress.md。

## 下一步

1. 查看 [Agent 提示词](../prompts/) 的完整版本
2. 参考 [文档模板](../templates/) 创建项目
3. 阅读 [最佳实践](best-practices.md) 避免常见错误
