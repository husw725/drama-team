# Drama Studio System Design (v2026-05-09)

> User requested a complete system: upload novel or input idea → configure style/episodes → full pipeline → short drama video output.
> Design document saved to `~/.hermes/tasks/drama-studio/DESIGN.md`.

## User Workflow

```
1. 用户点击「新建项目」→ 输入 Idea 或上传小说 → 选择风格/集数/时长
2. 点击「批量执行」→ 编剧层自动跑完（约 10-15 分钟）
3. 在画布上查看节点状态，点击节点查看内容
4. 用 AI 对话修改：「把主角改成男性」「加个反转」→ 自动重跑受影响节点
5. 编剧确认后，点击「开始制作」→ 生图→视频→配音→合成
6. 最终在预览面板观看成片
```

## 12-Phase Pipeline

```
📝 Input Layer
  1️⃣  input_analysis     Parse user input (novel/Idea/script)
  2️⃣  ip_analysis        World-building, theme, market positioning

📖 Screenwriting (Global, run once)
  3️⃣  outline            Three-act structure, episode summaries
  4️⃣  characters         Character settings (appearance/personality/relationships)
  5️⃣  visual_assets      Visual style definition (color palette/scenes/references)

🎬 Per-Episode (can run in parallel across episodes)
  6️⃣  script            Single episode script — ⚠️ Aligner review
  7️⃣  storyboard        Storyboard — ⚠️ Aligner review
  8️⃣  prompts           AI image generation prompts — ⚠️ Aligner review

🎨 Production (per episode, sequential)
  9️⃣  image_gen         Dreamina: character images + key frames
  🔟  video_gen         Seedance 2.0: video clips
  1️⃣1️⃣  dubbing         IndexTTS 2.0: voice dubbing
  1️⃣2️⃣  assembly        FFmpeg: video + audio + subtitles + BGM

```

## Dependency DAG

```
input_analysis
    └── ip_analysis
            └── outline
                    └── characters
                            └── visual_assets
                                    ├── script (EP-01) → storyboard → prompts → image_gen → video_gen → dubbing
                                    ├── script (EP-02) → storyboard → prompts → image_gen → video_gen → dubbing
                                    ├── script (EP-03) → storyboard → prompts → image_gen → video_gen → du