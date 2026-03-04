---
name: test-generator
description: |
  当用户想要为代码编写测试时使用此技能。根据函数签名和实现自动生成单元测试，
  覆盖正常路径、边界条件和异常情况。
  支持 TypeScript（Jest/Vitest）和 Python（pytest）。
  触发关键词：写测试、生成测试、test、单元测试、unit test、测试用例、
  帮我写个测试、补测试、test case、添加测试。
  即使用户只说"这个函数需要测试"，也应使用此技能。
---

# test-generator

根据代码自动生成高质量的单元测试，支持 Jest/Vitest（TypeScript）和 pytest（Python）。

## 输入

用户指定要测试的文件、函数或类。如果没有指定，分析最近修改的文件。

## 输出

完整的测试文件，可以直接运行。

## 执行步骤

1. 读取目标代码，分析函数签名、参数类型、返回值、依赖关系
2. 检测项目的测试框架：
   - 查看 package.json 判断 Jest 还是 Vitest
   - 查看 pyproject.toml / setup.cfg 判断 pytest 配置
   - 检查现有测试文件的风格和目录结构
3. 对每个函数/方法，生成以下类别的测试用例：

   **正常路径：**
   - 典型输入 → 预期输出
   - 多种合法输入的覆盖

   **边界条件：**
   - 空值/空数组/空字符串
   - 极大值/极小值
   - 单元素集合

   **异常路径：**
   - 非法输入（类型错误、格式错误）
   - 依赖服务不可用
   - 超时/并发场景

4. 生成测试代码，遵循项目现有风格：
   - TypeScript: describe/it 结构，合理使用 mock
   - Python: 类或函数式风格，使用 fixture 和 parametrize
5. 展示生成的测试，让用户确认后写入文件
6. 运行一次测试确认是否通过，如有失败则修复

## 测试模式参考

TypeScript（Jest/Vitest）和 Python（pytest）的完整测试代码示例，包括：
纯函数测试、异步函数测试、Mock 外部依赖、React 组件测试、Fixture、
Parametrize、FastAPI 端点测试、命名规范、测试维度覆盖清单，
详见 `references/test-patterns.md`。

生成测试时应参考该文件中的模式，保持风格一致。

## 注意事项

- 测试文件命名遵循项目已有约定（如 `*.test.ts`、`*.spec.ts`、`test_*.py`）
- mock 外部依赖（API 调用、数据库、文件系统），不要 mock 被测函数本身
- 每个 test case 只测一件事，命名要描述行为而非实现
- 如果函数有副作用，要测试副作用是否正确发生
- 不要生成无意义的"断言函数存在"之类的测试
