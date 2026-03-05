# auto-retry-loop

Ralph Wiggum 风格的自查自检循环，专为 Trae 等缺乏内置自动重试机制的 IDE 设计。

## 功能

当用户要求"做到测试通过"或"改到成功为止"时，持续迭代修改代码并运行验证，直到：
- 验证通过
- 达到最大重试次数（默认 5）
- 检测到连续重复失败（连续 3 次相同错误）

## 触发词

循环重试、做到通过、改到测试过、自己修到成功、retry until pass、自动重试、Ralph、自查自检、改到过为止、不要停直到通过。

## 灵感来源

澳洲放羊大叔 Geoffrey Huntley 的 5 行 Bash 脚本（Ralph Wiggum 循环），后被 Anthropic 收编为 Claude Code 官方插件。本 Skill 将相同思路规则化，适配 Trae 等 IDE。
