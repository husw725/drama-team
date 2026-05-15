#!/usr/bin/env node
/**
 * Drama Producer - 制作人启动脚本
 * 
 * 启动制作人 Agent，自动管理整个创作流程
 * 主会话启动后可以解放，由制作人自动管理
 */

const path = require('path');
const fs = require('fs');

class DramaProducer {
  constructor(projectPath) {
    this.projectPath = projectPath;
    this.skillsPath = path.join(__dirname, '..');
    this.config = {
      autoMode: true,
      reportInterval: 5,
      maxIterations: 5,
      qualityThreshold: 4.0,
      milestonePoints: [25, 50, 75, 100]
    };
  }

  /**
   * 启动制作人
   */
  async start() {
    console.log('\n' + '='.repeat(60));
    console.log('🎬 Drama Producer 启动');
    console.log('='.repeat(60));
    console.log('');

    // 1. 检查项目
    const projectInfo = this.checkProject();
    if (!projectInfo.valid) {
      console.error('❌ 项目检查失败:', projectInfo.error);
      return false;
    }

    // 2. 读取进度
    const progress = this.loadProgress();
    
    // 3. 显示当前状态
    this.showStatus(projectInfo, progress);

    // 4. 启动管理循环
    console.log('\n🚀 启动自动管理模式...\n');
    console.log('制作人将自动：');
    console.log('  ✅ 调度 Writer/Aligner/Recorder Agent');
    console.log('  ✅ 监控创作进度和质量');
    console.log('  ✅ 处理审核失败和迭代');
    console.log('  ✅ 定期汇报进度（每 5 集）');
    console.log('  ✅ 达到里程碑时通知');
    console.log('  ✅ 遇到问题主动提醒');
    console.log('');
    console.log('💡 主会话可以解放，制作人会自动管理');
    console.log('💡 需要进度时，随时询问制作人');
    console.log('');

    // 5. 返回启动信息
    return {
      status: 'ready',
      message: '制作人已启动，进入自动管理模式',
      projectInfo,
      progress,
      config: this.config
    };
  }

  /**
   * 检查项目
   */
  checkProject() {
    const requiredFiles = [
      'outline.md',
      'character.md',
      'episode-index.md'
    ];

    for (const file of requiredFiles) {
      const filePath = path.join(this.projectPath, file);
      if (!fs.existsSync(filePath)) {
        return {
          valid: false,
          error: `缺少必需文件: ${file}`
        };
      }
    }

    // 读取项目信息
    const outline = fs.readFileSync(
      path.join(this.projectPath, 'outline.md'),
      'utf-8'
    );

    // 提取剧名
    const titleMatch = outline.match(/#\s+(.+?)\s*$/m);
    const title = titleMatch ? titleMatch[1] : '未命名';

    // 提取集数
    const episodesMatch = outline.match(/(\d+)\s*集/);
    const totalEpisodes = episodesMatch ? parseInt(episodesMatch[1]) : 24;

    return {
      valid: true,
      title,
      totalEpisodes,
      path: this.projectPath
    };
  }

  /**
   * 加载进度
   */
  loadProgress() {
    const progressPath = path.join(this.projectPath, 'script.progress.md');
    
    if (!fs.existsSync(progressPath)) {
      return {
        completed: 0,
        total: 0,
        episodes: []
      };
    }

    const content = fs.readFileSync(progressPath, 'utf-8');
    
    // 解析进度（简化版）
    const completedMatch = content.match(/已完成.*?(\d+)\/(\d+)/);
    
    return {
      completed: completedMatch ? parseInt(completedMatch[1]) : 0,
      total: completedMatch ? parseInt(completedMatch[2]) : 0,
      episodes: []
    };
  }

  /**
   * 显示状态
   */
  showStatus(projectInfo, progress) {
    console.log('📋 项目信息');
    console.log('─'.repeat(60));
    console.log(`剧名: ${projectInfo.title}`);
    console.log(`总集数: ${projectInfo.totalEpisodes} 集`);
    console.log(`项目路径: ${projectInfo.path}`);
    console.log('');

    console.log('📊 当前进度');
    console.log('─'.repeat(60));
    
    const completed = progress.completed;
    const total = projectInfo.totalEpisodes;
    const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    console.log(`已完成: ${completed}/${total} 集 (${percent}%)`);
    
    // 进度条
    const barLength = 50;
    const filled = Math.round((percent / 100) * barLength);
    const bar = '█'.repeat(filled) + '░'.repeat(barLength - filled);
    console.log(`${bar} ${percent}%`);
    console.log('');

    if (completed > 0) {
      console.log('✅ 已完成剧集:');
      for (let i = 1; i <= completed; i++) {
        console.log(`   EP-${String(i).padStart(2, '0')}`);
      }
      console.log('');
    }

    if (completed < total) {
      console.log('⏳ 待创作:');
      console.log(`   EP-${String(completed + 1).padStart(2, '0')} ~ EP-${String(total).padStart(2, '0')} (${total - completed} 集)`);
      console.log('');
    }
  }

  /**
   * 生成启动命令
   */
  generateSpawnCommand() {
    return `
// 在 OpenClaw 中启动制作人
sessions_spawn({
  runtime: "subagent",
  mode: "session",  // 持续运行模式
  task: \`你是 Drama Team 的 Producer Agent。

请统筹管理《剧名》的创作工作：

## 职责
1. 自动调度 Writer/Aligner/Recorder Agent
2. 监控创作进度和质量
3. 处理审核失败和迭代
4. 定期汇报进度（每 5 集）
5. 达到里程碑时通知用户
6. 遇到问题主动提醒

## 工作模式
- 自动模式：无需主会话监控
- 定期上报：每完成 5 集汇报一次
- 里程碑通知：25%、50%、75%、100%
- 问题上报：迭代>3次、质量下降、重大问题

## 配置
- 最大迭代次数: 5
- 质量阈值: 4.0
- 汇报间隔: 5 集

请开始自动管理创作流程。\`,
  cwd: "${this.projectPath}"
})
`;
  }
}

// 命令行使用
if (require.main === module) {
  const projectPath = process.argv[2];
  
  if (!projectPath) {
    console.log('用法: node drama_producer.js <项目路径>');
    process.exit(1);
  }

  const producer = new DramaProducer(projectPath);
  producer.start().then(result => {
    if (result) {
      console.log('\n' + '='.repeat(60));
      console.log('📝 启动命令');
      console.log('='.repeat(60));
      console.log(producer.generateSpawnCommand());
    }
  });
}

module.exports = DramaProducer;
