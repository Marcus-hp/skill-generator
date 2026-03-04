# Skill 标准格式规范

本文档定义了一个合格 Skill 文件包的完整规范，供生成向导在起草内容时参考。

---

## 文件包结构

```
skill-name/
├── SKILL.md              必须。核心技能描述文件。
├── README.md             推荐。面向使用者的说明文档。
├── scripts/              可选。可执行脚本（Python / Bash）。
│   ├── __init__.py
│   └── main.py
├── references/           可选。按需加载的参考文档。
│   └── guide.md
├── assets/               可选。模板、素材、静态文件。
│   └── template.docx
└── evals/                可选。测试用例。
    ├── evals.json
    └── files/
        └── sample.pdf
```

---

## SKILL.md 结构

### YAML Frontmatter（必填字段）

```yaml
---
name: skill-name                  # 小写字母 + 连字符，唯一标识
description: |                    # 触发描述，80-120字为宜
  [技能功能描述]
  触发关键词：[中文关键词]，[英文关键词]
compatibility:                    # 可选
  dependencies: [lib1, lib2]      # Python 包或系统工具
  platforms: [claude-code, claude-ai]
---
```

### description 写作要点

description 是整个 Skill 最重要的字段，决定 Claude 何时调用它。

**必须包含：**
1. 这个技能**做什么**（功能描述）
2. **什么时候**应该触发（场景描述）
3. **触发关键词**（中英文都要有）

**推荐写法（稍微"积极"一些，防止欠触发）：**

```
当用户想要[做X]时使用此技能。
触发场景包括：[场景1]、[场景2]、[场景3]。
触发关键词：[中文词1]、[中文词2]、[英文词1]、[英文词2]。
即使用户没有明确提到"技能"，只要意图符合上述场景，也应使用此技能。
```

**不好的写法：**
```
# 太简短，触发不稳定
用于创建 Word 文档。
```

**好的写法：**
```
# 完整、明确、有关键词
当用户想要创建、编辑或生成 Word 文档、报告、合同、简历时使用此技能。
触发关键词：Word文档、写报告、生成文档、.docx、合同模板、简历。
包括从零生成文档，或基于已有内容重新排版格式的需求。
```

---

### SKILL.md 正文结构

```markdown
# [技能名称]

[一句话简介，说明这个技能的核心价值]

## 输入

[描述用户通常会提供什么，格式是什么]

## 输出

[描述最终交付什么，文件还是文字，格式要求]

## 执行步骤

1. [第一步，动词开头]
2. [第二步]
3. ...

## 注意事项

- [边界条件1]
- [边界条件2]
（如无特殊限制可省略此节）
```

---

## 三层加载机制

Skill 采用按需加载设计：

| 层级 | 内容 | 何时加载 |
|------|------|---------|
| 第1层 | YAML frontmatter（name + description） | 始终在上下文中，约100字 |
| 第2层 | SKILL.md 正文 | 技能被触发时加载，建议控制在500行以内 |
| 第3层 | scripts/ references/ assets/ | 执行时按需读取，不限大小 |

**实践建议：**
- SKILL.md 保持精简，只放"入口指令"
- 大段背景知识放进 `references/`，需要时用 `view` 读取
- 复杂逻辑写成脚本放进 `scripts/`，需要时执行

---

## references/ 目录规范

- 每个文件聚焦一个主题
- 超过 300 行的文件要加目录
- 在 SKILL.md 中明确说明"何时读取哪个文件"

## scripts/ 目录规范

- 必须有 `__init__.py`（Python 包）
- 每个脚本职责单一
- 脚本顶部注释说明用途、输入参数、输出结果

## assets/ 目录规范

- 存放不会被修改的静态文件
- 文件名要有描述性，如 `report-template.docx` 而非 `template1.docx`

---

## evals/ 测试用例格式

```json
{
  "skill_name": "skill-name",
  "evals": [
    {
      "id": 1,
      "prompt": "用户的示例请求",
      "expected_output": "期望输出的描述",
      "files": ["evals/files/sample.pdf"],
      "expectations": [
        "输出包含 X",
        "生成了 Y 格式的文件"
      ]
    }
  ]
}
```
