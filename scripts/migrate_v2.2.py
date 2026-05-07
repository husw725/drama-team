#!/usr/bin/env python3
"""
v2.2 Migration Script Template for Short Drama Projects

Usage:
  cp ~/.hermes/skills/creative/hermes-short-drama-team/scripts/migrate_v2.2.py /path/to/project/
  # Edit SCENES, PROPS, SCENE_KEYWORDS, PROP_KEYWORDS for your project
  python3 migrate_v2.2.py

What it does:
1. Creates visual_assets/manifest.md (角色外观 + 场景视觉 + 道具清单)
2. Generates scene reference prompts (纯环境无角色)
3. Generates prop reference prompts (静物特写)
4. Scans all prompts/ EP-XX.md files, extracts image/video prompts
5. Assigns scene_ref (S-XX) and prop_refs ([P-XX, ...]) to each frame
6. Parses characters, scripts, storyboards
7. Writes project_data.json with v2.2 structure
8. Creates visual_assets/manifest.md

Then run:
  cp ~/.hermes/tasks/carmilla-20260428/build_html.py /path/to/project/
  python3 build_html.py
"""
import os, json, re

# ====== EDIT THIS ======
BASE = os.path.expanduser('~/.hermes/tasks/YOUR-PROJECT')

# Define your scenes from characters.md / MASTER.md
SCENES = [
    {"id": "S-01", "name": "Scene Name", "desc": "Full visual description for reference image..."},
    # ... add all unique scenes
]

# Define key props (跨集出现、需要一致性的道具)
PROPS = [
    {"name": "Prop Name", "desc": "Visual description", "episodes": "EP-01, EP-05"},
    # ... add all key props
]

# Keyword → scene mapping for automatic frame classification
SCENE_KEYWORDS = {
    'S-01': ['keyword1', 'keyword2'],
    # ...
}

# Keyword → prop mapping for automatic prop injection
PROP_KEYWORDS = {
    'P-01': ['keyword1', 'keyword2'],
    # ...
}

# Episode range defaults (for frames that don't match keywords)
def default_scene(ep_num):
    if ep_num <= 5: return 'S-01'
    elif ep_num <= 14: return 'S-07'
    # ... customize per project
    return 'S-09'

# ====== TEMPLATE CODE BELOW (do not edit) ======

def gen_scene_prompt(scene):
    style = scene.get('style', 'Semi-realistic Korean manga style')
    return f"{style}, 9:16 vertical, wide establishing shot, no characters, environmental scene reference, {scene['desc']}"

for s in SCENES:
    s['prompt'] = gen_scene_prompt(s)
    s['status'] = 'pending'

def gen_prop_prompt(prop):
    style = prop.get('style', 'Semi-realistic Korean manga style')
    return f"{style}, close-up still life, no characters, prop reference, {prop['desc']}, candlelit"

for i, p in enumerate(PROPS, 1):
    p['id'] = f"P-{i:02d}"
    p['prompt'] = gen_prop_prompt(p)
    p['status'] = 'pending'

# Parse all prompts
prompts_dir = os.path.join(BASE, 'prompts')
all_episodes = []

for fname in sorted(os.listdir(prompts_dir)):
    if not fname.endswith('.md'):
        continue
    with open(os.path.join(prompts_dir, fname), 'r', encoding='utf-8') as f:
        content = f.read()
    
    ep_id = fname.replace('.md', '')
    ep_num = int(ep_id.split('-')[1])
    
    # Image prompts
    image_prompts = []
    for m in re.finditer(r'### Frame (\d+): (.+?)\n\*\*Prompt:\*\*(.*?)(?=\n\n### |\n---|\Z)', content, re.DOTALL):
        prompt_text = m.group(3).strip()
        prompt_lower = prompt_text.lower()
        
        scene_ref = default_scene(ep_num)
        for sid, keywords in SCENE_KEYWORDS.items():
            for kw in keywords:
                if kw in prompt_lower:
                    scene_ref = sid
                    break
        
        prop_refs = []
        for pid, keywords in PROP_KEYWORDS.items():
            for kw in keywords:
                if kw in prompt_lower:
                    prop_refs.append(pid)
                    break
        
        image_prompts.append({
            'frame': int(m.group(1)),
            'time': m.group(2).strip(),
            'scene_ref': scene_ref,
            'prop_refs': prop_refs,
            'prompt': prompt_text,
            'status': 'pending',
        })
    
    # Video prompts
    video_prompts = []
    for m in re.finditer(r'### Shot (\d+): (.+?)\n\*\*Prompt:\*\*(.*?)(?=\n\n### |\n---|\Z)', content, re.DOTALL):
        video_prompts.append({
            'shot': int(m.group(1)),
            'timeRange': m.group(2).strip(),
            'prompt': m.group(3).strip(),
        })
    
    title_m = re.search(r'# ' + ep_id + r':\s*(.+?)(?:\s*-\s*AI)?', content)
    title = title_m.group(1).strip() if title_m else ep_id
    
    all_episodes.append({
        'id': ep_id, 'title': title,
        'prompts': {'imagePrompts': image_prompts, 'videoPrompts': video_prompts},
    })

# Parse characters
char_path = os.path.join(BASE, 'characters', 'characters.md')
characters = []
if os.path.exists(char_path):
    with open(char_path, 'r', encoding='utf-8') as f:
        char_md = f.read()
    for m in re.finditer(r'### \d+\.\s+(.+?)\n(.+?)(?=### |\Z)', char_md, re.DOTALL):
        name = m.group(1).strip()
        body = m.group(2).strip()
        attrs = {}
        for am in re.finditer(r'(?:\*\*[^*]+\*\*:\s*|.*)', body):
            line = am.group(0).strip()
            if ':' in line:
                key, _, val = line.partition(':')
                attrs[key.strip().replace('**', '')] = val.strip()
        characters.append({'name': name, 'attrs': attrs})

# Parse scripts
script_dir = os.path.join(BASE, 'script')
screenplays = {}
if os.path.isdir(script_dir):
    for fname in sorted(os.listdir(script_dir)):
        if not fname.endswith('.md'): continue
        with open(os.path.join(script_dir, fname), 'r', encoding='utf-8') as f:
            script_md = f.read()
        ep_id = fname.replace('.md', '')
        scenes_data = []
        for m in re.finditer(r'## Scene Breakdown\n(.+?)(?=## |\Z)', script_md, re.DOTALL):
            lines = [l for l in m.group(1).split('\n') if '|' in l and '---' not in l]
            for line in lines[1:]:
                cols = [c.strip() for c in line.split('|')[1:-1]]
                if len(cols) >= 4:
                    scenes_data.append({'Time':cols[0],'Scene':cols[1],'Action':cols[2],'Dialogue':cols[3]})
        dialogue = []
        for m in re.finditer(r'## Key Dialogue\n(.+?)(?=## |\Z)', script_md, re.DOTALL):
            lines = [l for l in m.group(1).split('\n') if '|' in l and '---' not in l]
            for line in lines[1:]:
                cols = [c.strip().strip('"') for c in line.split('|')[1:-1]]
                if len(cols) == 2:
                    dialogue.append({'EN':cols[0],'CN':cols[1]})
        cliff_m = re.search(r'## Cliffhanger\n\n?(.+?)(?=## |\Z)', script_md, re.DOTALL)
        screenplays[ep_id] = {'scenes':scenes_data,'dialogue':dialogue,'cliffhanger':cliff_m.group(1).strip() if cliff_m else ''}

# Parse storyboards
sb_dir = os.path.join(BASE, 'storyboard')
if os.path.isdir(sb_dir):
    for ep in all_episodes:
        sb_path = os.path.join(sb_dir, f'{ep["id"]}.md')
        if not os.path.exists(sb_path): continue
        with open(sb_path, 'r', encoding='utf-8') as f:
            sb_md = f.read()
        shots = []
        for m in re.finditer(r'## Key Frames\n(.+?)(?=## |\Z)', sb_md, re.DOTALL):
            lines = [l for l in m.group(1).split('\n') if '|' in l and '---' not in l]
            for line in lines[1:]:
                cols = [c.strip() for c in line.split('|')[1:-1]]
                if len(cols) >= 8:
                    shots.append({'#':cols[0],'Time':cols[1],'Shot':cols[2],'Camera':cols[3],
                                   'Duration':cols[4],'Description':cols[5],'Characters':cols[6],'Lighting':cols[7]})
        ep['storyboard'] = {'shots': shots}

# Write project_data.json
project_data = {
    'episodes': all_episodes, 'characters': characters,
    'manifest': {}, 'screenplays': screenplays,
    'scenes': SCENES, 'props': PROPS,
}
out_path = os.path.join(BASE, 'project_data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(project_data, f, ensure_ascii=False, indent=2)

# Create visual_assets/manifest.md
va_dir = os.path.join(BASE, 'visual_assets')
os.makedirs(va_dir, exist_ok=True)
manifest_md = "# 视觉资产清单 (Visual Asset Manifest)\n\n> 此文档是所有AI生图Prompt的视觉基准。\n\n"
manifest_md += "## 场景视觉\n\n"
for s in SCENES:
    manifest_md += f"### {s['id']}: {s['name']}\n- **描述**: {s['desc']}\n\n"
manifest_md += "## 道具清单\n\n| 道具名 | 描述 | 出现集数 |\n|--------|------|---------|\n"
for p in PROPS:
    manifest_md += f"| {p['name']} | {p['desc']} | {p['episodes']} |\n"
with open(os.path.join(va_dir, 'manifest.md'), 'w', encoding='utf-8') as f:
    f.write(manifest_md)

# Summary
total_img = sum(len(ep['prompts']['imagePrompts']) for ep in all_episodes)
total_vid = sum(len(ep['prompts']['videoPrompts']) for ep in all_episodes)
print(f"v2.2 Migration Complete:")
print(f"  Scenes: {len(SCENES)} | Props: {len(PROPS)}")
print(f"  Episodes: {len(all_episodes)} | Frames: {total_img} | Shots: {total_vid}")
print(f"  Saved: {out_path} ({os.path.getsize(out_path)/1024:.0f}KB)")
