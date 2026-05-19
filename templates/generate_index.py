#!/usr/bin/env python3
"""Parse project files into project_data.json for the SPA index page.

Dual-format parser: supports both Hollywood screenplay (code block) 
and legacy table format scripts. Handles VO-only episodes without 
Key Dialogue tables.

Copy to project root and run: python3 generate_index.py
"""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))

def read(path):
    p = os.path.join(BASE, path)
    if not os.path.exists(p): return ''
    with open(p, 'r', encoding='utf-8') as f: return f.read()

def parse_table(text):
    lines = [l for l in text.split('\n') if l.strip().startswith('|') and not all(c in '-_' for c in l.strip().split('|')[1] if c.strip())]
    if len(lines) < 2: return []
    headers = [h.strip() for h in lines[0].split('|')[1:-1]]
    rows = []
    for line in lines[1:]:
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) == len(headers): rows.append(dict(zip(headers, cells)))
    return rows

def parse_script(md):
    """Parse both Hollywood screenplay (code block) and legacy table format."""
    result = {'screenplay': '', 'scenes': [], 'dialogue': [], 'voiceovers': []}
    
    # Title
    m = re.search(r'# EP-(\d+): (.+?)(?:\s*\|)', md)
    if m: result['id'], result['title'] = f'EP-{m.group(1)}', m.group(2).strip()
    
    # Hollywood screenplay (code block)
    m = re.search(r'```\n(.*?)\n```', md, re.DOTALL)
    if m:
        result['screenplay'] = m.group(1).strip()
        for sm in re.finditer(r'(EXT\.|INT\.)\s+(.+?)\s*[-—](.+?)(?:\n|$)', result['screenplay'], re.IGNORECASE):
            result['scenes'].append({'type': sm.group(1), 'location': sm.group(2), 'time': sm.group(3)})
    
    # Legacy table format
    for m in re.finditer(r'## Scene Breakdown\n(.+?)(?=##|$)', md, re.DOTALL):
        for line in [l for l in m.group(1).split('\n') if '|' in l and '---' not in l][1:]:
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 5: result['scenes'].append({'Time':cols[0],'Scene':cols[1],'Action':cols[2],'Dialogue (EN/CN)':cols[3],'BGM':cols[4]})
    
    # Key Dialogue (may be absent)
    for m in re.finditer(r'## Key Dialogue\n(.+?)(?=##|$)', md, re.DOTALL):
        for line in [l for l in m.group(1).split('\n') if '|' in l and '---' not in l][1:]:
            cols = [c.strip().strip('"') for c in line.split('|')[1:-1]]
            if len(cols) == 2: result['dialogue'].append({'EN':cols[0],'CN':cols[1]})
    
    # Voiceovers
    for m in re.finditer(r'## Voiceovers\n(.+?)(?=##|$)', md, re.DOTALL):
        for line in m.group(1).strip().split('\n'):
            vo_m = re.match(r'-\s*VOICEOVER\s*\((\w+)\)\s*(.*)', line.strip(), re.DOTALL)
            if vo_m: result['voiceovers'].append({'speaker': vo_m.group(1), 'text': vo_m.group(2).strip()})
    
    return result

def parse_storyboard(md):
    result = {'shots': [], 'notes': [], 'stats': {}}
    m = re.search(r'# EP-(\d+): (.+?)\s*—?\s*Storyboard', md)
    if m: result['id'], result['title'] = f'EP-{m.group(1)}', m.group(2).strip()
    
    m = re.search(r'## Key Frames \((\d+) shots\) \| Duration: (\d+)s \| Type: (\w+)', md)
    if m: result['stats'] = {'shots': int(m.group(1)), 'duration': int(m.group(2)), 'type': m.group(3)}
    
    # Parse shots table (v3.1: 8 or 12 columns — dynamic header detection)
    # Match the full table including header line
    m = re.search(r'(\| # \| Time .+?\|)\n\|[-| ]+\n(.+?)(?=##|$)', md, re.DOTALL)
    if m:
        header_line = m.group(1)
        body_lines = m.group(2)
        headers = [h.strip() for h in header_line.split('|')[1:-1]]
        for line in body_lines.strip().split('\n'):
            if not line.strip().startswith('|'): continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) == len(headers):
                result['shots'].append(dict(zip(headers, cells)))
            elif len(cells) >= len(headers):
                shot_dict = dict(zip(headers, cells[:len(headers)]))
                result['shots'].append(shot_dict)
    
    m = re.search(r'## Shot Notes\n\n?(.*?)(?=$)', md, re.DOTALL)
    if m:
        for line in m.group(1).strip().split('\n'):
            line = line.strip().lstrip('- ')
            if line: result['notes'].append(line)
    return result

def parse_prompts(md):
    result = {'chars': [], 'scenes': [], 'imagePrompts': [], 'videoPrompts': []}
    m = re.search(r'# EP-(\d+): (.+?)\s*-\s*AI Prompts', md)
    if m: result['id'], result['title'] = f'EP-{m.group(1)}', m.group(2).strip()
    
    for m in re.finditer(r'### Characters in This Episode:\n(.*?)(?=###|$)', md, re.DOTALL):
        for cm in re.finditer(r'\*\*(.+?)\*\*:\s*(.+?)(?=\n\*\*|$)', m.group(1)):
            result['chars'].append({'name': cm.group(1).strip(), 'desc': cm.group(2).strip()})
    
    for m in re.finditer(r'### Scenes in This Episode:\n(.*?)(?=\n\n### |\Z)', md, re.DOTALL):
        result['scenes'] = [s.strip() for s in m.group(1).strip().split() if s.strip()]
    
    for m in re.finditer(r'### Frame (\d+): (.+?)\n\*\*Prompt:\*\*(.*?)(?=\n\n### |\Z)', md, re.DOTALL):
        refs = re.findall(r'\[ref:\s*(S-\d+|P-\d+)\]', m.group(3))
        result['imagePrompts'].append({'frame':int(m.group(1)),'time':m.group(2).strip(),'prompt':m.group(3).strip(),'refs':refs})
    
    for m in re.finditer(r'### Shot (\d+): (.+?)\n\*\*Prompt:\*\*(.*?)(?=\n\n### |\Z)', md, re.DOTALL):
        result['videoPrompts'].append({'shot':int(m.group(1)),'timeRange':m.group(2).strip(),'prompt':m.group(3).strip()})
    
    return result

def parse_characters(md):
    chars = []
    for m in re.finditer(r'### (.+?)\n\n((?:- .+\n?)+)', md):
        attrs = {}
        for am in re.finditer(r'- \*\*(.+?)\*\*:\s*(.+?)(?:\n|$)', m.group(2)):
            attrs[am.group(1).strip()] = am.group(2).strip()
        chars.append({'name': m.group(1).strip(), 'attrs': attrs})
    return chars

def main():
    data = {'episodes': [], 'characters': [], 'manifest': {}, 'scene_prop_data': {}}
    
    sp_path = os.path.join(BASE, 'scene_prop_data.json')
    if os.path.exists(sp_path):
        with open(sp_path, 'r', encoding='utf-8') as f: data['scene_prop_data'] = json.load(f)
    
    chars_md = read('characters.md')
    if chars_md: data['characters'] = parse_characters(chars_md)
    
    for ep_num in range(1, 37):
        ep_id = f'EP-{ep_num:02d}'
        script_md = read(f'script/{ep_id}.md')
        sb_md = read(f'storyboard/{ep_id}.md')
        pr_md = read(f'prompts/{ep_id}.md')
        
        ep = {'id': ep_id, 'script': parse_script(script_md) if script_md else {},
               'storyboard': parse_storyboard(sb_md) if sb_md else {},
               'prompts': parse_prompts(pr_md) if pr_md else {}}
        
        if not ep['script'].get('title'):
            ep['script']['title'] = ep['storyboard'].get('title') or ep['prompts'].get('title', '')
        if not ep['prompts'].get('title'):
            ep['prompts']['title'] = ep['script'].get('title') or ep['storyboard'].get('title', '')
        
        data['episodes'].append(ep)
    
    out = os.path.join(BASE, 'project_data.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    total_img = sum(len(ep['prompts'].get('imagePrompts', [])) for ep in data['episodes'])
    total_vid = sum(len(ep['prompts'].get('videoPrompts', [])) for ep in data['episodes'])
    total_shots = sum(len(ep['storyboard'].get('shots', [])) for ep in data['episodes'])
    print(f"Parsed {len(data['episodes'])} episodes, {len(data['characters'])} characters")
    print(f"Scenes: {len(data['scene_prop_data'].get('scenes',[]))}, Props: {len(data['scene_prop_data'].get('props',[]))}")
    print(f"Total: {total_shots} shots, {total_img} image prompts, {total_vid} video prompts")
    print(f"JSON saved to {out} ({os.path.getsize(out)//1024}KB)")

if __name__ == '__main__':
    main()
