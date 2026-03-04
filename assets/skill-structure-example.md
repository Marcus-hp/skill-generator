# 示例：一个完整的 Skill 文件包长什么样

这个文件展示了一个生产级 Skill 的完整样例，供生成向导参考和向用户展示。

---

## 示例：pdf-reader（PDF 内容提取技能）

### 文件结构

```
pdf-reader/
├── SKILL.md
├── README.md
├── scripts/
│   ├── __init__.py
│   └── extract.py
├── references/
│   └── guide.md
└── evals/
    ├── evals.json
    └── files/
        └── sample.pdf
```

### SKILL.md 示例

```markdown
---
name: pdf-reader
description: |
  当用户想要读取、提取或分析 PDF 文件内容时使用此技能。
  触发场景：提取 PDF 文字、分析 PDF 报告、从 PDF 获取数据。
  触发关键词：PDF、读取PDF、提取内容、解析文档、pdf内容。
  即使用户只是上传了 PDF 并描述任务，也应主动使用此技能。
compatibility:
  dependencies: [pdfplumber, PyPDF2]
---

# pdf-reader

从 PDF 文件中提取文字、表格和结构化内容。

## 输入

用户上传 PDF 文件，或提供 PDF 文件路径。

## 输出

提取后的文字内容，以及识别到的表格数据（Markdown 格式）。

## 执行步骤

1. 接收 PDF 文件，检查文件是否可读
2. 运行 `scripts/extract.py` 提取文字和表格
3. 对提取内容进行结构化整理
4. 将结果展示给用户，并询问是否需要进一步处理

## 注意事项

- 扫描版 PDF（图片型）需要 OCR，提取质量可能较低
- 加密 PDF 无法直接提取，需要密码
- 超过 100 页的文件建议分段处理
```

---

这是一个清晰、完整、实用的 Skill 样例。注意：
- description 包含了功能、场景、关键词三要素
- 执行步骤引用了具体脚本（`scripts/extract.py`）
- 注意事项简洁明了，说明了真实的限制
