# Conventional Commits 完整规范

## 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Type 类型（必选）

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat(auth): add Google OAuth login |
| `fix` | 修复 bug | fix(cart): resolve quantity update race condition |
| `refactor` | 重构（不改变行为） | refactor(api): extract validation middleware |
| `docs` | 文档修改 | docs: update API endpoint descriptions |
| `test` | 测试相关 | test(auth): add JWT expiration edge cases |
| `chore` | 构建/依赖/工具 | chore: upgrade TypeScript to 5.4 |
| `style` | 格式调整（不影响逻辑） | style: fix indentation in auth module |
| `perf` | 性能优化 | perf(query): add index for user lookup |
| `ci` | CI/CD 配置 | ci: add staging deployment workflow |
| `revert` | 回退提交 | revert: feat(auth): add Google OAuth login |

## Scope 范围（可选）

从项目目录结构或模块名推断，常见模式：

- 按功能模块：`auth`, `cart`, `payment`, `user`
- 按技术层：`api`, `db`, `ui`, `config`
- 按文件类型：`deps`, `docker`, `ci`

**规则：**
- 全小写
- 不超过 15 个字符
- 不确定时可以省略

## Subject 描述（必选）

- 英文，全小写开头
- 祈使语气（add 而不是 added / adds）
- 不超过 50 个字符
- 不加句号结尾
- 描述 what，不描述 how

**好的写法：**
```
feat(auth): add JWT token refresh mechanism
fix(upload): handle file size exceeding limit
refactor(api): extract common error handler
```

**差的写法：**
```
feat(auth): Added JWT token refresh mechanism.    # 过去式 + 句号
fix: fixed bug                                      # 太模糊
update code                                         # 没有 type，无意义
```

## Body 正文（可选）

- 解释 **why**，不解释 what（what 看 diff 就知道）
- 换行限制 72 字符
- 可以用 markdown 列表

```
fix(cart): resolve quantity update race condition

When two requests update the same cart item simultaneously,
the second request could overwrite the first one's quantity.

Added optimistic locking with version check to prevent this.
```

## Footer 尾部（可选）

**Breaking Change（破坏性变更）：**
```
feat(api): change auth endpoint response format

BREAKING CHANGE: /api/auth/login now returns { token, user }
instead of { access_token, refresh_token, user_data }.
Clients need to update their response parsing logic.
```

**关联 Issue：**
```
fix(login): handle expired session redirect

Closes #234
Refs #220
```

## 多改动拆分原则

一次提交只做一件事。判断标准：

| 场景 | 拆 or 不拆 |
|------|-----------|
| 修了一个 bug | 一次提交 |
| 修了一个 bug + 顺手格式化了代码 | 拆成两次（fix + style） |
| 新功能 + 对应的测试 | 一次提交（feat） |
| 重构 + 修复了重构过程发现的 bug | 拆成两次（refactor + fix） |
| 升级依赖 + 适配 API 变更 | 一次提交（chore），body 里说明 |

## 敏感文件检查清单

提交前必须检查以下文件是否误包含：

- `.env` / `.env.local` / `.env.production`
- `credentials.json` / `serviceAccountKey.json`
- `*.pem` / `*.key` / `*.p12`
- `id_rsa` / `id_ed25519`
- 包含 API key、token、password 的配置文件
