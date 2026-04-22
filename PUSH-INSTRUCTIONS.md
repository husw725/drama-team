# GitHub 推送指南

项目已经准备好推送到 GitHub，但需要认证。请选择以下一种方式：

## 方式 1: 使用 GitHub Personal Access Token (推荐)

1. 生成 Token:
   - 访问 https://github.com/settings/tokens
   - 点击 "Generate new token"
   - 选择权限：`repo` (完整仓库控制)
   - 复制生成的 Token

2. 使用 Token 推送:
```bash
cd /mnt/c/Users/melot/openclaw-drama-team-learning
git remote set-url origin https://husw725:<YOUR_TOKEN>@github.com/husw725/drama-team.git
git push -u origin main
```

## 方式 2: 在 Windows 中使用 Git Bash

1. 打开 Git Bash (Windows)
2. 运行以下命令:
```bash
cd /c/Users/melot/openclaw-drama-team-learning
git push -u origin main
```
3. 在弹出的窗口中输入 GitHub 用户名和密码 (或 PAT)

## 方式 3: 使用 GitHub Desktop

1. 打开 GitHub Desktop
2. 选择目录：`C:/Users/melot/openclaw-drama-team-learning`
3. 点击 "Push to origin"

## 方式 4: 手动推送 (如果其他方式都失败)

1. 在 Windows 文件资源管理器中打开：
   `C:/Users/melot/openclaw-drama-team-learning`

2. 右键点击空白处，选择 "Git Bash Here"

3. 运行:
```bash
git push -u origin main
```

4. 在浏览器中完成认证

---

## 项目信息

- **仓库**: https://github.com/husw725/drama-team
- **分支**: main
- **文件数**: 17 个
- **提交信息**: "feat: 初始发布 - 多 Agent 协作短剧编剧系统"

## 推送后的检查清单

- [ ] 访问 https://github.com/husw725/drama-team 确认文件已上传
- [ ] 检查 README.md 显示正确
- [ ] 验证所有文档和示例文件都在
- [ ] 设置仓库为 Public 或 Private (根据需要)
- [ ] 添加 Topics 标签：`ai`, `drama`, `scriptwriting`, `multi-agent`
