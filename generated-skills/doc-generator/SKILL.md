---
name: doc-generator
description: |
  当用户需要生成项目文档时使用此技能。包括 README、API 文档、
  变更日志、函数注释和模块说明文档。根据代码自动生成，不需要手写。
  触发关键词：生成文档、写文档、README、API docs、changelog、
  文档、documentation、帮我写个说明、添加注释、JSDoc、docstring。
  即使用户只说"这个项目需要个 README"，也应使用此技能。
---

# doc-generator

根据代码自动生成各类项目文档。

## 输入

用户指定要生成的文档类型，或者指定要为哪些代码添加文档注释。

## 输出

完整的文档文件或代码注释。

## 执行步骤

1. 确定文档类型：
   - **README.md**：项目整体说明
   - **API 文档**：接口列表、请求/响应格式
   - **CHANGELOG.md**：基于 git log 生成变更日志
   - **代码注释**：JSDoc / docstring / 类型注释
   - **模块文档**：某个模块的详细说明
2. 根据类型收集信息：

   **README：**
   - 读取 package.json / pyproject.toml 获取项目信息
   - 扫描目录结构
   - 读取主入口文件理解项目用途
   - 检查已有的 scripts 命令

   **API 文档：**
   - 扫描路由定义（Express routes / FastAPI endpoints）
   - 提取请求参数和响应类型
   - 读取中间件了解认证方式

   **CHANGELOG：**
   - 读取 git log，按 Conventional Commits 分类
   - 按版本分组

   **代码注释：**
   - 读取函数签名和实现
   - 生成 JSDoc（TS）或 docstring（Python）

3. 生成文档，遵循以下格式：
   - README: 标题 → 简介 → 安装 → 使用 → 配置 → 开发 → 许可证
   - API: 按模块分组，每个接口包含 URL、方法、参数、响应、示例
   - 代码注释: 描述、参数、返回值、异常、示例
4. 展示给用户确认后写入文件

## 注意事项

- README 不要过度详细，保持简洁实用
- API 文档要包含请求/响应示例，不要只有类型定义
- 代码注释只给公开 API 添加，内部实现不需要逐行注释
- 生成的文档要和项目现有文档风格保持一致
- CHANGELOG 基于实际的 git 历史，不要编造内容
