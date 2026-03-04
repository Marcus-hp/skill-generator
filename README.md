# Skill Generator — 交互式 Agent Skill 生成向导

通过对话问答，引导你一步步创建完整的 Agent Skill 文件包。
内含 **22 个预置技能** 和 **自动编排规则**，覆盖开发效率、架构设计、产品管理全链路。

## 项目结构

```
skill-generator/
├── SKILL.md                        核心技能描述（向导行为指南）
├── README.md                       本文件
├── pyproject.toml                  依赖管理
├── conftest.py                     测试配置
├── .gitignore                      Git 忽略规则
│
├── scripts/                        核心脚本
│   ├── create_skill.py             自动创建文件包
│   ├── session_manager.py          会话进度管理
│   ├── error_handler.py            错误处理和用户提示
│   ├── intelligent_recommender.py  智能推荐系统
│   ├── skill_preview.py            技能预览和实时编辑
│   ├── skill_updater.py            技能更新和版本管理
│   └── skill_validator.py          配置验证机制
│
├── references/                     参考规范
│   ├── skill-format.md             Skill 标准格式规范
│   ├── templates.md                各类型技能预设模板
│   ├── error-handling.md           错误处理规范
│   ├── preview-and-edit.md         技能预览和实时编辑规范
│   ├── skill-update-guide.md       技能更新管理规范
│   └── validation-rules.md         配置验证机制规范
│
├── assets/
│   └── skill-structure-example.md  完整技能包示例
│
├── evals/
│   └── evals.json                  测试用例
│
├── generated-skills/               22 个预置技能（详见下方）
│   ├── git-commit-standard/
│   ├── code-review-assistant/
│   ├── test-generator/
│   ├── ...
│   └── security-checker/
│
├── .cursor/rules/                  Cursor 编排规则
│   ├── orchestrator.mdc            任务编排器
│   ├── skill-registry.mdc          技能注册表
│   └── quality-gate.mdc            质量关卡
│
├── prototype/                      原型输出目录
│   └── crud-admin.html             示例原型
│
└── test_basic_functionality.py     单元测试（pytest）
```

## 预置技能一览（22 个）

### 开发效率（10 个）

| 技能 | 说明 | 附加资源 |
|------|------|---------|
| git-commit-standard | Git 提交规范化，自动生成 Conventional Commits | `references/commit-convention.md` |
| code-review-assistant | 代码审查，覆盖安全/性能/类型/规范 | `references/review-checklist.md` |
| test-generator | 自动生成单元测试（Jest/Vitest/pytest） | `references/test-patterns.md` |
| error-diagnostics | 报错诊断，定位根因并给出修复建议 | — |
| api-doc-lookup | API 和文档快速查询 | — |
| sql-assistant | SQL 生成、优化和解释 | — |
| refactor-helper | 代码重构（提取函数、拆模块、消除重复） | — |
| doc-generator | 自动生成 README、API 文档、Changelog | — |
| env-config-template | Docker/CI/CD/Linter 配置一键生成 | `assets/` 下 5 个标准模板 |
| i18n-helper | 国际化/本地化辅助 | — |

### 架构能力（3 个）

| 技能 | 说明 | 附加资源 |
|------|------|---------|
| system-design-advisor | 系统设计辅助（选型、拆分、缓存、MQ） | `references/design-patterns.md` |
| performance-optimizer | 性能优化诊断（前端/后端/数据库） | `references/optimization-playbook.md` |
| security-checker | 安全检查（OWASP Top 10、漏洞修复） | `references/security-checklist.md` |

### 产品能力（8 个）

| 技能 | 说明 | 附加资源 |
|------|------|---------|
| prd-writer | PRD 需求文档生成 | `assets/prd-template.md` |
| story-breakdown | 用户故事拆解 | — |
| prototype-spec | 原型规格说明 | — |
| prototype-builder | 交互式原型生成（HTML） | — |
| data-insight | 数据分析洞察 | — |
| competitive-analysis | 竞品分析 | — |
| release-notes | 发版记录生成 | — |
| meeting-notes | 会议纪要整理 | — |

### 带附加资源的技能（8 个增强版）

以下技能除了 `SKILL.md` + `README.md`，还包含参考文档或模板，提升输出一致性：

| 技能 | 附加文件 | 内容 |
|------|---------|------|
| git-commit-standard | `references/commit-convention.md` | Conventional Commits 完整规范 |
| code-review-assistant | `references/review-checklist.md` | TS + Python 检查清单 |
| test-generator | `references/test-patterns.md` | 测试代码模式参考 |
| env-config-template | `assets/*.template` | Dockerfile、docker-compose、CI、.env 模板 |
| prd-writer | `assets/prd-template.md` | PRD 文档固定模板 |
| system-design-advisor | `references/design-patterns.md` | 架构模式与选型参考 |
| performance-optimizer | `references/optimization-playbook.md` | 性能优化手册 |
| security-checker | `references/security-checklist.md` | 安全检查清单 + 漏洞修复代码 |

## 编排规则（Cursor）

`.cursor/rules/` 下的 3 个规则文件在 Cursor 中自动生效：

| 规则 | 作用 |
|------|------|
| `orchestrator.mdc` | 自动拆解任务、匹配 Skill、编排执行顺序 |
| `skill-registry.mdc` | 22 个 Skill 的触发词和路径映射表 |
| `quality-gate.mdc` | 编码后自动质量检查、提交前规范验证 |

AI 收到任务后会自动判断规模 → 匹配相关 Skill → 并行或串行执行 → 过质量关卡。

## 使用方式

### 在 Cursor 中

直接开始工作，编排规则会自动加载。例如：

- "帮我做一个用户注册功能" → 自动编排设计、编码、测试、审查
- "提交" → 自动生成规范化 commit message
- "检查一下" → 自动执行代码审查 + 安全检查 + 性能检测
- "写个 PRD" → 自动使用 PRD 模板引导生成

### 在 Claude Code 中

将项目放到 `.claude/skills/` 目录下，说"帮我创建一个新的 Skill"即可启动向导。

### 复用技能到其他项目

将 `generated-skills/` 下的任意技能文件夹复制到目标项目即可使用。

## 技术栈

- Python 3.10+
- jsonschema（配置验证）
- pytest + pytest-cov（测试）

## 安装开发依赖

```bash
pip install -e ".[dev]"
```

## 运行测试

```bash
pytest -v
```
