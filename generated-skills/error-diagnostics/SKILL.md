---
name: error-diagnostics
description: |
  当用户遇到代码报错、异常信息或运行失败时使用此技能。自动解析错误信息，
  定位根因，提供修复方案。支持 TypeScript/Node.js 和 Python 错误。
  触发关键词：报错、error、bug、异常、崩溃、失败、跑不起来、TypeError、
  ImportError、traceback、stack trace、这是什么错误、怎么修。
  即使用户只贴了一段错误信息没有说别的，也应使用此技能。
---

# error-diagnostics

解析错误信息，定位原因，提供修复方案。

## 输入

用户提供以下任意一种：
- 直接粘贴的错误信息/stack trace
- 报错的截图描述
- "运行 xxx 命令报错了"

## 输出

结构化的诊断报告，包含原因分析和可直接执行的修复方案。

## 执行步骤

1. 解析错误信息，提取关键要素：
   - 错误类型（TypeError / ImportError / SyntaxError 等）
   - 出错位置（文件名 + 行号）
   - 调用链/stack trace
2. 读取出错位置的源代码及上下文（前后 20 行）
3. 分析可能的原因，按可能性排序：

   **TypeScript/Node.js 常见错误：**
   - 类型不匹配、null/undefined 未处理
   - 导入路径错误、循环依赖
   - 异步操作未 await、Promise 未捕获
   - 版本不兼容（Node/npm 包）

   **Python 常见错误：**
   - 类型错误、AttributeError
   - 导入错误、模块找不到
   - 缩进错误、语法错误
   - 虚拟环境/依赖未安装

4. 输出诊断报告：
   ```
   ## 错误诊断

   **错误类型：** TypeError
   **位置：** src/auth.ts:42
   **原因：** user 可能为 null，但未做空值检查

   ## 修复方案

   方案 1（推荐）：添加空值检查
   方案 2：使用可选链操作符

   需要我帮你修复吗？
   ```
5. 用户确认后直接修复代码

## 注意事项

- 如果错误信息不完整，主动要求用户提供完整的 stack trace
- 先判断是代码问题还是环境问题（依赖未装、版本不对）
- 对于环境问题，给出具体的命令而不是笼统的建议
- 如果涉及第三方库的 bug，给出对应的 GitHub Issue 链接或 workaround
