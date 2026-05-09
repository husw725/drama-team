# Drama Studio Pipeline API Implementation

> Implemented 2026-05-09 at `~/.hermes/tasks/drama-studio/`. Turns the 6-stage drama-team workflow into an async REST + WebSocket API.

## Architecture

```
Client (WS/REST)
  │
  ├── POST /api/phases/:id/run  →  pipeline.runPhase()
  ├── POST /api/phases/:id/cancel
  └── WS execute_phase message  →  pipeline.runPhase()
                                    │
                                    ├── gatherUpstreamContext()  [dependency map]
                                    ├── callAI()                 [vLLM via OpenAI API]
                                    ├── alignerLoop()            [max 3 rounds: review → rewrite]
                                    └── store.updateProject()    [persist to JSON]
                                    │
                                    └── wsBroadcast()            [phase_started / progress / completed / error]
```

## File Layout

```
server/
  prompts.ts              # System prompts per phase (extracted from drama-team skill)
  services/
    ai.ts                 # callAI() — vLLM OpenAI-compatible API
    pipeline.ts           # Pipeline orchestrator: runPhase(), alignerLoop(), cancelPhase()
  routes/
    project.ts            # CRUD for /api/projects
    phase.ts              # Phase execution: /api/phases/:id/run, /cancel, /order
  store/
    store.ts              # In-memory Map + JSON file persistence
  ws.ts                   # wsBroadcast() helper
  index.ts                # Express + WS server, wires phaseRouter
shared/
  types.ts                # ProjectData, PhaseStatus, PhaseName, etc.
```

## Key Design Decisions

### 1. Prompts as extracted strings, not inline

`server/prompts.ts` holds all system prompts as `export const` strings, extracted directly from the drama-team skill. This makes them:
- Reviewable as a single file
- Testable independently
- Updatable when the skill evolves

### 2. Pipeline is async fire-and-forget

`runPhase()` returns immediately. All progress updates are broadcast via `wsBroadcast()`. The REST endpoint returns `{ ok: true, message: 'started' }` without waiting for completion.

### 3. Upstream context via dependency map

`PHASE_DEPENDENCIES` encodes the DAG:
```ts
const PHASE_DEPENDENCIES: Record<string, PhaseName[]> = {
  ip_analysis: [],
  outline: ['ip_analysis'],
  characters: ['outline'],
  visual_assets: ['characters', 'outline'],
  script: ['outline', 'characters', 'visual_assets'],
  storyboard: ['script'],
  prompts: ['storyboard', 'characters', 'visual_assets'],
  // ...
};
```
`gatherUpstreamContext()` walks this map and concatenates completed phase content.

### 4. Aligner loop for phases that need it

`ALIGNER_PHASES = new Set(['script', 'storyboard', 'prompts'])` — only these phases run the review loop:
1. Generate content
2. Call `alignerReview()` with Aligner v4.0 prompt + content + visual assets
3. Parse score from `**总分: XX/100**`
4. If score < 80 and round < 3: rewrite with feedback, loop
5. If score ≥ 80 or max rounds: accept

### 5. Per-episode phases

Script/storyboard/prompts are per-episode. `episodeId` parameter gates:
- REST endpoint: `POST /api/phases/:id/run { phase, episode_id }`
- WS message: `{ type: 'execute_phase', payload: { projectId, phase, episodeId } }`
- Store: phase status stored with `episode_id` field
- Multiple episodes can run concurrently (different `episodeId` = different in-flight tracker)

## WebSocket Protocol (Phase Events)

```ts
// Server → Client
{ type: 'phase_started',      payload: { projectId, phase, episodeId, log } }
{ type: 'phase_progress',      payload: { projectId, phase, step, message } }
{ type: 'phase_aligner_review', payload: { projectId, phase, round } }
{ type: 'phase_aligner_result', payload: { projectId, phase, round, score, passed, review } }
{ type: 'phase_completed',     payload: { projectId, phase, episodeId, contentLength, log } }
{ type: 'phase_error',         payload: { projectId, phase, error, cancelled, log } }
{ type: 'phase_cancelled',     payload: { projectId, phase, episodeId } }
{ type: 'phase_suggest_next',  payload: { projectId, currentPhase, currentEpisode, nextEpisode } }
```

## Integration with index.ts

```ts
// Import
import phaseRouter from './routes/phase';
import { runPhase } from './services/pipeline';

// Mount REST route
app.use('/api/phases', phaseRouter);

// Wire WS handler
case 'execute_phase': {
  runPhase(projectId, phase, episodeId || undefined).catch(err => {
    wsBroadcast('phase_error', { projectId, phase, error: err.message });
  });
  break;
}
```

## ES Compatibility Pitfall

- `regex.match(/pattern/s)` (dotall flag) requires ES2018+. The drama-studio `tsconfig.json` targets ES2022 but tsx/tsx may resolve differently in some environments.
- **Fix**: Use `[\s\S]` instead of `.` with `/s` flag:
  ```ts
  // ❌ ES2018+ only
  review.match(/\*\*修改建议:?\*\*(.+?)(?=\n\n|\Z)/s)
  // ✅ ES2015 compatible
  review.match(/\*\*修改建议:?\*\*([\s\S]+?)(?=\n\n|\Z)/)
  ```

## Storyboard 0 字符 Bug (2026-05-09 发现)

- **症状**：Storyboard 阶段运行 6.7 分钟，返回 `content: ""`（0 字符），log 只有 start 一条
- **可能原因**：`gatherUpstreamContext()` 注入的上下文过大。Storyboard 依赖 script（3KB+），script 依赖 outline+characters+visual_assets（合计 ~10KB），加上 system prompt 可能超出模型有效处理窗口
- **修复方向**：
  1. 在 `gatherUpstreamContext()` 中截断上游内容（保留最近 3 阶段，每阶段限制 2000 字符）
  2. 或将上游内容改为摘要形式（让 AI 先生成 200 字摘要再注入）
  3. 或增加 AI 调用的超时时间（当前默认 timeout 可能不足）
- **临时方案**：QA 测试时跳过 storyboard，先测试 prompts

## Server Crash: EADDRINUSE (2026-05-09 发现)

- **症状**：`tsx server/index.ts` 启动后报 `EADDRINUSE: address already in use :::3000`
- **原因**：旧进程残留（前一次启动因异常退出但端口未释放）
- **修复**：启动前 `pkill -f "tsx server/index.ts"` 清理旧进程
- **建议**：在 `server/index.ts` 中加入端口检查/优雅关闭处理

## Verification

```bash
cd ~/.hermes/tasks/drama-studio
node_modules/.bin/tsx --no-warnings -e "import('./server/prompts.ts').then(() => console.log('OK'))"
node_modules/.bin/tsx --no-warnings -e "import('./server/services/pipeline.ts').then(() => console.log('OK'))"
node_modules/.bin/tsx --no-warnings -e "import('./server/routes/phase.ts').then(() => console.log('OK'))"
timeout 5 node_modules/.bin/tsx --no-warnings server/index.ts  # starts, prints port, exits
```
