---
name: i18n-helper
description: |
  当用户需要处理国际化和本地化时使用此技能。扫描代码中的硬编码字符串，
  提取为 i18n key，生成翻译文件，管理多语言内容。
  支持 react-i18next、next-intl、vue-i18n、Python gettext 等方案。
  触发关键词：国际化、本地化、i18n、l10n、多语言、翻译、translation、
  internationalization、localization、语言切换。
  即使用户只说"这个页面要支持英文"，也应使用此技能。
---

# i18n-helper

代码国际化辅助：提取硬编码字符串、生成翻译文件、管理多语言内容。

## 输入

以下任意一种：
- 指定文件/目录进行硬编码字符串扫描
- 已有的翻译文件需要补充新语言
- 描述国际化方案需求

## 输出

更新后的代码（硬编码替换为 i18n key）和翻译文件。

## 执行步骤

1. 检测项目使用的 i18n 方案：
   - package.json 中检查 react-i18next / next-intl / vue-i18n
   - Python 项目检查 gettext / babel 配置
   - 如果没有现成方案，推荐适合项目的方案
2. 扫描指定文件/目录，找出所有硬编码的用户可见字符串：
   - JSX/TSX 中的文本节点
   - placeholder、label、title 等属性值
   - 错误提示信息
   - Python 中的用户提示文字
   - 排除：日志信息、开发调试信息、注释
3. 生成 i18n key 命名方案：
   ```
   ## 发现的硬编码字符串

   | 文件 | 行号 | 原文 | 建议 key |
   |------|------|------|----------|
   | Login.tsx:12 | "请输入密码" | login.passwordPlaceholder |
   | Login.tsx:18 | "登录" | login.submitButton |
   | Header.tsx:5 | "首页" | nav.home |

   确认后开始替换？
   ```
4. 用户确认后：
   - 将硬编码字符串替换为 i18n 函数调用（如 `t('login.submitButton')`）
   - 生成/更新翻译文件（JSON / PO 格式）
   - 如果需要多语言，为每种语言生成模板
5. 检查替换后代码是否正确（括号匹配、变量插值等）

## 注意事项

- key 的命名要有层级结构，按页面/模块分组
- 包含变量插值的字符串要使用 i18n 框架的插值语法
- 复数形式、日期格式等要使用 i18n 框架的内置支持
- 不要翻译代码中的技术术语（如 "API key"、"token"）
- 翻译文件按语言代码命名（zh-CN.json、en-US.json）
