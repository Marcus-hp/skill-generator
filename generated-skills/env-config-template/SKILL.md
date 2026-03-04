---
name: env-config-template
description: |
  当用户需要配置开发环境、CI/CD 流程或项目基础设施时使用此技能。
  生成 Docker、docker-compose、GitHub Actions、ESLint、Prettier、
  pyproject.toml 等配置文件。
  触发关键词：Docker、dockerfile、docker-compose、CI、CD、GitHub Actions、
  配置、config、eslint、prettier、环境配置、部署、deploy、linter。
  即使用户只说"帮我配个 Docker"，也应使用此技能。
---

# env-config-template

一键生成开发环境和 CI/CD 配置文件，适配 TypeScript 和 Python 项目。

## 输入

用户描述需要的配置类型。

## 输出

可直接使用的配置文件。

## 执行步骤

1. 识别配置需求和项目类型：
   - 读取 package.json → TypeScript/Node 项目
   - 读取 pyproject.toml → Python 项目
   - 两者都有 → 全栈项目
2. 根据需求生成对应配置：

   **Docker 相关：**
   - Dockerfile（多阶段构建，区分 dev/prod）
   - docker-compose.yml（含数据库、缓存等依赖服务）
   - .dockerignore

   **CI/CD（GitHub Actions）：**
   - 测试流水线（lint → test → build）
   - 部署流水线（区分 staging/production）
   - PR 检查（自动运行测试 + 代码审查）

   **代码质量工具：**
   - ESLint + Prettier 配置（TypeScript）
   - Ruff / Black / isort 配置（Python）
   - husky + lint-staged（pre-commit 钩子）

   **环境变量：**
   - .env.example（列出所有必需的环境变量和说明）
   - .env.local 模板

3. 检查项目已有配置，避免冲突或覆盖
4. 生成配置文件，添加关键注释说明
5. 展示给用户确认后写入

## 预置模板

`assets/` 目录下提供了标准化的配置模板，生成配置时以这些模板为基础，根据项目实际情况调整：

| 模板文件 | 用途 |
|---------|------|
| `assets/dockerfile-node.template` | Node.js 多阶段构建 Dockerfile |
| `assets/dockerfile-python.template` | Python 多阶段构建 Dockerfile |
| `assets/docker-compose.template.yml` | docker-compose（含 Postgres + Redis） |
| `assets/github-actions-ci.template.yml` | GitHub Actions CI 流水线 |
| `assets/env-example.template` | .env.example 标准模板 |

使用时读取对应模板，替换其中的占位变量并根据项目需求增删配置项。

## 注意事项

- Docker 镜像使用 alpine 版本减小体积
- CI/CD 配置要缓存依赖安装步骤，加速流水线
- 不要在配置中硬编码密钥，使用环境变量或 secrets
- 生成 .env.example 时不要包含真实的密钥值
- 配置要适配项目的 Node/Python 版本
