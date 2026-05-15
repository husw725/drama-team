#!/usr/bin/env node
/**
 * Drama Team - OpenClaw 多 Agent 协作实现
 * 
 * 使用 OpenClaw 的 sessions_spawn 启动独立 Agent
 */

const fs = require('fs');
const path = require('path');

class DramaTeam {
  constructor(projectPath) {
    this.projectPath = projectPath;
    this.skillsPath = path.join(__dirname, '..');
  }

  /**
   * 创作一集剧本（多 Agent 协作）
   * 
   * @param {number} epNum - 集数
   * @param {number} maxIterations - 最大迭代次数
   * @returns {Promise<boolean>} - 是否成功
   */
  async createEpisode(epNum, maxIterations = 5) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`开始创作 EP-${String(epNum).padStart(2, '0')}`);
    console.log('='.repeat(60));
    console.log('');

    // 读取上下文
    const context = this.loadContext();

    // 迭代创作
    for (let iteration = 1; iteration <= maxIterations; iteration++) {
      console.log(`\n${'='.repeat(50)}`);
      console.log(`EP-${String(epNum).padStart(2, '0')} - 第 ${iteration} 次迭代`);
      console.log('='.repeat(50));
      console.log('');

      // 1. Writer Agent 创作
      console.log('[1/3] Writer Agent 正在创作...');
      const script = await this.callWriterAgent(epNum, context, iteration);

      // 2. Aligner Agent 审核
      console.log('[2/3] Aligner Agent 正在审核...');
      const result = await this.callAlignerAgent(script);

      if (result.status === 'PASS') {
        console.log('[3/3] ✅ 审核通过！');

        // 3. Recorder Agent 记录
        console.log('\n[Recorder] 正在记录进度...');
        await this.callRecorderAgent(epNum, script, iteration);

        // 保存剧本
        this.saveScript(epNum, script);

        console.log(`\n✅ EP-${String(epNum).padStart(2, '0')} 创作完成！`);
        return true;
      } else {
        console.log('[3/3] ❌ 审核未通过');
        console.log(`\n反馈：${result.feedback}`);

        // 更新上下文（加入反馈）
        context.feedback = result.feedback;
        context.suggestions = result.suggestions || [];

        if (iteration < maxIterations) {
          console.log(`\n⏭️  继续第 ${iteration + 1} 次迭代...`);
        }
      }
    }

    console.log(`\n⚠️  达到最大迭代次数 (${maxIterations})，建议人工介入`);
    return false;
  }

  /**
   * 加载项目上下文
   */
  loadContext() {
    const context = {};

    const outlinePath = path.join(this.projectPath, 'outline.md');
    if (fs.existsSync(outlinePath)) {
      context.outline = fs.readFileSync(outlinePath, 'utf-8');
    }

    const characterPath = path.join(this.projectPath, 'character.md');
    if (fs.existsSync(characterPath)) {
      context.characters = fs.readFileSync(characterPath, 'utf-8');
    }

    const episodeIndexPath = path.join(this.projectPath, 'episode-index.md');
    if (fs.existsSync(episodeIndexPath)) {
      context.episodeIndex = fs.readFileSync(episodeIndexPath, 'utf-8');
    }

    return context;
  }

  /**
   * 调用 Writer Agent
   * 
   * 实际实现应该使用 sessions_spawn：
   * sessions_spawn({
   *   runtime: "acp",
   *   agentId: "drama-writer",
   *   task: "创作剧本",
   *   cwd: this.projectPath,
   *   attachments: [...]
   * })
   */
  async callWriterAgent(epNum, context, iteration) {
    const writerPrompt = fs.readFileSync(
      path.join(this.skillsPath, 'prompts/writer.md'),
      'utf-8'
    );

    const task = `
你现在是 Drama Team 的 Writer Agent。

请根据以下信息创作 EP-${String(epNum).padStart(2, '0')} 剧本：

## 项目上下文
- 大纲：见附件 outline.md
- 人物设定：见附件 character.md
- 集目录：见附件 episode-index.md

## 创作法则
${writerPrompt}

${iteration > 1 && context.feedback ? `
## 上次审核反馈
${context.feedback}

请根据反馈修改剧本。
` : ''}

## 输出要求
- 按照 templates/episode.md 格式输出
- 保存为 EP-${String(epNum).padStart(2, '0')}.md
`;

    // 实际调用 sessions_spawn
    // 这里返回任务描述，供实际使用
    return {
      task,
      agent: 'drama-writer',
      context
    };
  }

  /**
   * 调用 Aligner Agent
   * 
   * 实际实现应该使用 sessions_spawn
   */
  async callAlignerAgent(script) {
    const alignerPrompt = fs.readFileSync(
      path.join(this.skillsPath, 'prompts/aligner.md'),
      'utf-8'
    );

    const task = `
你现在是 Drama Team 的 Aligner Agent。

请审核以下剧本：

## 审核标准
${alignerPrompt}

## 待审核剧本
${script}

## 输出格式
返回 JSON：
{
  "status": "PASS 或 FAIL",
  "score": 4.5,
  "feedback": "具体反馈",
  "suggestions": ["修改建议1", "修改建议2"]
}
`;

    // 实际调用 sessions_spawn
    return {
      task,
      agent: 'drama-aligner',
      expectedOutput: {
        status: 'PASS 或 FAIL',
        score: 'number',
        feedback: 'string',
        suggestions: 'array'
      }
    };
  }

  /**
   * 调用 Recorder Agent
   */
  async callRecorderAgent(epNum, script, iterations) {
    const recorderPrompt = fs.readFileSync(
      path.join(this.skillsPath, 'prompts/recorder.md'),
      'utf-8'
    );

    const task = `
你现在是 Drama Team 的 Recorder Agent。

请记录以下创作进度：

## Recorder 职责
${recorderPrompt}

## 本次创作
- 集数：EP-${String(epNum).padStart(2, '0')}
- 迭代次数：${iterations}
- 状态：PASS

## 任务
更新 script.progress.md 文件
`;

    // 实际调用 sessions_spawn
    return {
      task,
      agent: 'drama-recorder'
    };
  }

  /**
   * 保存剧本
   */
  saveScript(epNum, script) {
    const scriptPath = path.join(
      this.projectPath,
      `EP-${String(epNum).padStart(2, '0')}.md`
    );
    console.log(`保存到：${scriptPath}`);
  }
}

// 导出
module.exports = DramaTeam;

// 命令行使用
if (require.main === module) {
  const projectPath = process.argv[2];
  const epNum = parseInt(process.argv[3]) || 1;

  if (!projectPath) {
    console.log('用法: node drama_team.js <项目路径> [集数]');
    console.log('示例: node drama_team.js my-drama 1');
    process.exit(1);
  }

  const team = new DramaTeam(projectPath);
  team.createEpisode(epNum).then(success => {
    process.exit(success ? 0 : 1);
  });
}
