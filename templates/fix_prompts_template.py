#!/usr/bin/env python3
"""
批量修复帧级 Prompt 的场景描述和道具注入.
用法: 修改 SCENE_MAP / PROP_KEYWORDS / SCENE_INFERENCE, 改 base 路径, 然后运行.

工作流程:
1. 解析剧本表格 → 建立 S-XX→场景名映射
2. 从动作关键词推断场景变化（当 S-XX 无显式场景名时）
3. 场景继承：一旦推断出场景切换，后续行继承新场景
4. 按帧 start 时间最近匹配脚本行（不用重叠面积！）
5. 替换 scene: [...] 描述 + 注入道具

2026-04-29 在 Carmilla 项目上验证通过（30集, 580+ 帧）
"""
import os, re

base = os.path.expanduser("~/.hermes/tasks/YOUR_PROJECT")

# === 1. 场景描述映射表 ===
# (中文关键词, 完整英文场景描述)
SCENE_MAP = [
    ("Laura卧室", "Gothic Victorian bedroom, cool candlelight tones, heavy velvet curtains, carved bedposts, antique mirror, bedside candlestick, stone walls"),
    ("卧室", "Gothic Victorian bedroom, ..."),
    ("古堡走廊", "Gothic castle corridor, stone walls, wall-mounted candlesticks, carpet, moonlight, cool blue-gray tones"),
    ("走廊", "Gothic castle corridor, ..."),
    # ... 根据你的项目添加所有场景
]

DEFAULT_SCENE_NAME = "卧室"

# === 2. 场景推断（动作关键词 → 场景名）===
# 当脚本行只有 S-XX（无场景名）时，从动作描述推断
SCENE_INFERENCE = [
    ("走廊", "走廊"), ("冲开门", "走廊"), ("打开门", "走廊"),
    ("走廊空", "走廊空荡"), ("门外闪过", "走廊"),
    ("花园", "花园"), ("走出", "城堡外"),
    ("大厅", "大厅"), ("书房", "书房"), ("楼梯", "楼梯"),
    ("厨房", "厨房"), ("墓园", "墓园"), ("废墟", "废墟"),
    ("仪式", "仪式室"),
    # ... 添加你项目的场景推断关键词
]

# === 3. 道具映射（中文动作关键词 → 英文道具描述）===
PROP_KEYWORDS = {
    "镜子": "ornate antique full-length mirror with carved frame",
    "日记": "leather-bound diary with faded ink writing",
    "茶杯": "porcelain teacup on a wooden table",
    "照片": "old sepia-toned photograph in a silver frame",
    "匕首": "ornate silver dagger with engraved handle",
    "窗户": "tall Gothic arched window with moonlight streaming through",
    "脚印": "wet footprints on stone floor slowly evaporating",
    "蜡烛": "ornate brass candlestick with flickering candle",
    "书": "ancient leather-bound books on wooden shelves",
    "床": "carved Victorian ornate bed with tall posts and white sheets",
    # ... 添加更多道具
}

def resolve_scene(sn):
    if not sn:
        return SCENE_MAP[0][1]
    for cn, desc in SCENE_MAP:
        if cn in sn:
            return desc
    return SCENE_MAP[0][1]

def infer_scene(action, prev_scene_name):
    for kw, scene_name in SCENE_INFERENCE:
        if kw in action:
            return scene_name
    return prev_scene_name

def find_props(action):
    props = []
    for kw, desc in PROP_KEYWORDS.items():
        if kw in action and desc not in props:
            props.append(desc)
    return props

def parse_time_range(t):
    m = re.match(r'(\d+)-(\d+)s', t.strip())
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)

def parse_script_scenes(ep_file):
    """解析脚本表格，建立 S-XX→name 映射 + 场景继承."""
    text = open(ep_file, "r", encoding="utf-8").read()
    table_section = text.split("## Scene Breakdown")[1] if "## Scene Breakdown" in text else ""
    for em in ["## Key Dialogue", "## Cliffhanger", "## Aligner", "## Notes"]:
        if em in table_section:
            table_section = table_section.split(em)[0]

    sxx_map = {}
    raw_rows = []

    for line in table_section.split("\n"):
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 4:
            continue
        if "Time" in cells[0] or cells[1] in ("Scene", "Action", "Dialogue"):
            continue

        scene_raw = cells[1].strip()
        scene_m = re.match(r"(S-\d+)\s*(.*)", scene_raw)
        if scene_m:
            sxx_id, scene_name = scene_m.group(1), scene_m.group(2).strip()
            if scene_name and sxx_id not in sxx_map:
                sxx_map[sxx_id] = scene_name

        time_m = re.match(r'(\d+)-(\d+)s', cells[0].strip())
        start, end = (int(time_m.group(1)), int(time_m.group(2))) if time_m else (None, None)
        raw_rows.append({"start": start, "end": end, "scene_raw": scene_raw, "action": cells[2].strip()})

    # 场景继承：一旦推断出场景切换，S-XX映射更新，后续行继承新场景
    prev_scene_name = DEFAULT_SCENE_NAME
    for row in raw_rows:
        scene_m = re.match(r"(S-\d+)\s*(.*)", row["scene_raw"])
        if not scene_m:
            row["scene_name"] = prev_scene_name
            continue
        sxx_id, explicit_name = scene_m.group(1), scene_m.group(2).strip()
        if explicit_name:
            prev_scene_name = explicit_name
            row["scene_name"] = explicit_name
        else:
            mapped_name = sxx_map.get(sxx_id, "")
            if mapped_name:
                inferred = infer_scene(row["action"], mapped_name)
                if inferred != mapped_name:
                    sxx_map[sxx_id] = inferred
                    prev_scene_name = inferred
                else:
                    prev_scene_name = mapped_name
                row["scene_name"] = prev_scene_name
            else:
                inferred = infer_scene(row["action"], prev_scene_name)
                sxx_map[sxx_id] = inferred
                prev_scene_name = inferred
                row["scene_name"] = inferred

    return rows

def match_frame_to_script(frame_start, script_rows):
    """用帧 start 时间匹配最近的脚本行（不要用重叠面积！）."""
    best_row, best_dist = None, float('inf')
    for row in script_rows:
        if row["start"] is None:
            continue
        dist = abs(frame_start - row["start"])
        if dist < best_dist:
            best_dist, best_row = dist, row
    return best_row

def fix_prompts(ep_num):
    ep = f"EP-{ep_num:02d}"
    script_path = f"{base}/script/{ep}.md"
    prompt_path = f"{base}/prompts/{ep}.md"
    if not os.path.exists(prompt_path) or not os.path.exists(script_path):
        return

    prompt = open(prompt_path, "r", encoding="utf-8").read()
    script_rows = parse_script_scenes(script_path)

    frame_pattern = r'(### Frame (\d+): ([\d\-]+s.*?)\n\*\*Prompt:\*\*)(.*?)(?=\n###|\Z)'

    def fix_frame(m):
        prefix, time_str, existing = m.group(1), m.group(3).strip(), m.group(4).strip()
        fs, fe = parse_time_range(time_str)
        if fs is None:
            return prefix + "\n" + existing

        row = match_frame_to_script(fs, script_rows)
        if not row:
            return prefix + "\n" + existing

        scene_desc = resolve_scene(row["scene_name"])
        props = find_props(row["action"])
        props_str = ", ".join(props)

        new = re.sub(r'scene: \[[^\]]+\]', f'scene: [{scene_desc}]', existing)
        if props_str:
            target = f"scene: [{scene_desc}]"
            ip = new.find(target)
            if ip >= 0:
                insert_pos = ip + len(target)
                already = all(
                    any(pw.lower() in new.lower() for pw in prop.split()[:3])
                    for prop in props
                )
                if not already:
                    new = new[:insert_pos] + ", " + props_str + new[insert_pos:]

        return prefix + "\n" + new

    new_prompt = re.sub(frame_pattern, fix_frame, prompt, flags=re.DOTALL)
    open(prompt_path, "w", encoding="utf-8").write(new_prompt)

# === 运行 ===
for ep in range(1, 31):  # 修改集数范围
    fix_prompts(ep)
    print(f"  EP-{ep:02d}: done")
print("All prompts fixed!")
