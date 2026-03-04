---
name: git-commit-standard
description: |
  当用户完成代码修改想要提交时使用此技能。自动分析 git diff，生成符合
  Conventional Commits 规范的提交信息。
  触发关键词：提交、commit、git commit、帮我提交、写个 commit message、
  提交代码、push、提交信息、commit message。
  即使用户只说"提交一下"，也应使用此技能。
---

# git-commit-standard

根据 git diff 自动生成规范化的 commit message，遵循 Conventional Commits 规范。

## 输入

用户完成代码修改后说"提交"或"commit"。可能附带简短描述说明改了什么。

## 输出

一条或多条结构化的 commit message，等待用户确认后执行 git commit。

## 执行步骤

1. 运行 `git status` 和 `git diff --staged`（如果没有 staged 内容则用 `git diff`）查看所有变更
2. 分析变更内容，判断变更类型：
   - `feat`: 新功能
   - `fix`: 修复 bug
   - `refactor`: 重构（不改变行为）
   - `docs`: 文档修改
   - `test`: 测试相关
   - `chore`: 构建、依赖等杂项
   - `style`: 格式调整（不影响逻辑）
   - `perf`: 性能优化
   - `ci`: CI/CD 配置
3. 如果变更涉及多个不相关的改动，建议拆分为多次提交，并给出每次提交应包含哪些文件
4. 生成 commit message，格式为：
   ```
   <type>(<scope>): <简短描述>

   <可选的详细说明，解释 why 而不是 what>
   ```
5. 展示给用户确认：
   ```
   建议的提交信息：

   feat(auth): add JWT token refresh mechanism

   1️⃣  确认，直接提交
   2️⃣  我来修改
   3️⃣  拆分为多次提交
   ```
6. 用户确认后执行 `git add` 和 `git commit`

## 参考规范

完整的 Conventional Commits 规范、type 定义、scope 命名、body/footer 格式、多改动拆分原则、
敏感文件检查清单，详见 `references/commit-convention.md`。

## 注意事项

- scope 从目录结构或模块名推断，不要生造
- 描述用英文，保持简洁（50 字符以内）
- 如果用户明确要求中文 commit message，也要遵守
- 不要自动 push，提交后提示用户是否需要 push
- 如果发现 .env、credentials 等敏感文件在变更中，必须警告用户（详见 `references/commit-convention.md` 敏感文件清单）
