# 上传仓库指南

以下步骤适用于将本地代码上传到 Git 托管平台（如 GitHub、Gitee）：

1. **初始化仓库（若尚未初始化）**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **添加远程地址**
   ```bash
   git remote add origin <远程仓库地址>
   ```
   常见格式：
   - SSH：`git@github.com:username/repo.git`
   - HTTPS：`https://github.com/username/repo.git`

3. **推送代码**
   ```bash
   git push -u origin main
   ```
   - 如果远程默认分支是 `master`，将命令中的 `main` 改为 `master`。
   - 若远程已存在历史且本地分支需要合并，先拉取再推送：
     ```bash
     git pull --rebase origin main
     git push
     ```

4. **常见问题**
   - 推送被拒绝（`non-fast-forward`）：说明远程有新的提交，本地需先 `git pull --rebase`。
   - 权限/认证问题：检查是否配置 SSH Key 或使用了正确的访问令牌。
   - 大文件受限：可使用 `.gitignore` 排除不需要追踪的文件，或使用 Git LFS 处理大文件。

5. **更新后续变更**
   每次修改后重复：
   ```bash
   git add <修改的文件或目录>
   git commit -m "描述本次修改"
   git push
   ```

