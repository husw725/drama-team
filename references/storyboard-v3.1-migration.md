# Storyboard v3.1 Migration — 2026-05-15 导演反馈

## 触发原因

导演反馈 Carmilla 分镜缺少四个维度：场景引用、氛围、音效/音乐、环境光（只写了特效光）。

## 格式变更

| 维度 | v3.0 (旧) | v3.1 (新) |
|------|-----------|-----------|
| 表头列数 | 8 列 | 12 列 |
| Scene | ❌ 无 | ✅ `S-XX 场景名` 从剧本映射 |
| Atmosphere | ❌ 无 | ✅ 每镜头 2-4 个氛围词 |
| Lighting | 1-2 个词（只写特效光） | 三层：主光(来源)+补光(来源+颜色)+效果 |
| SFX | ❌ 无 | ✅ 环境音+动作音 |
| BGM | ❌ 无 | ✅ 具体可执行音乐描述 |

**新版 12 列表头：**
```
| # | Time | Scene | Shot | Camera | Duration | Description | Characters | Atmosphere | Lighting | SFX | BGM |
```

## 解析器修复

`generate_index.py` 的 `parse_storyboard` 硬编码了旧 8 列表头：
```python
# ❌ 旧代码 — 8 列硬编码
header_line = '| # | Time | Shot | Camera | Duration | Description | Characters | Lighting |'
```

已改为动态表头检测（兼容 8 列和 12 列）：
```python
# ✅ 新代码 — 动态检测
m = re.search(r'(\| # \| Time .+?\|)\n\|[-| ]+\n(.+?)(?=##|$)', md, re.DOTALL)
headers = [h.strip() for h in m.group(1).split('|')[1:-1]]
```

## 审核标准升级

| 旧 (7维) | 新 (9维) |
|----------|----------|
| 镜头密度 20% | 镜头密度 18% |
| 冲突密度 15% | **灯光完整性 10%** (NEW) |
| 对白节奏 10% | **氛围动态性 8%** (NEW) |
| 景别 15% | 冲突密度 8% |
| 运镜 15% | 对白节奏 6% |
| 叙事 10% | 景别 10% |
| 悬念 10% | 运镜 10% |
| | 叙事 8% |
| | 悬念 6% |
| | **SFX/BGM 覆盖率 6%** (NEW) |
| | **场景引用 10%** (NEW) |

## 迁移步骤（新项目）

1. 新分镜直接套用 v3.1 模板（已在技能中）
2. `generate_index.py` 从模板复制（已更新）
3. 项目旧分镜如需迁移：批量重跑分镜生成（从剧本重新生成）

## 已知遗留

- 项目级 `~/.hermes/tasks/carmilla-20260428/generate_index.py` 仍用旧 8 列硬编码，需手动 patch
- 现有 32 集分镜文件仍为旧 8 列格式，如需升级需重新生成
