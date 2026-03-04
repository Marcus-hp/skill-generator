# Skill 预设模板库

当用户选择某种技能类型时，使用对应模板作为起草基础，再根据用户的具体描述调整。
智能推荐系统会根据用户描述自动选择最合适的模板并填充内容。

---

## 智能模板匹配

系统会根据用户描述自动识别技能类型并推荐对应模板：

**识别关键词映射：**
- 文件处理：文档、文件、word、pdf、excel、ppt、报告、表格
- 数据分析：数据、分析、统计、图表、可视化、csv、数据集  
- 代码辅助：代码、编程、开发、bug、调试、优化、重构
- 搜索研究：研究、调研、搜索、了解、分析、报告、对比
- 流程自动化：自动化、批量、流程、工作流、重复、执行

---

## 模板 1：文件处理类（增强版）

适用场景：生成/处理 Word、PDF、Excel、PPT 等文件。

```yaml
name: [file-type]-creator
description: |
  当用户想要创建或处理[文件类型]文件时使用此技能。
  触发场景包括：生成报告、制作模板、格式转换、批量处理文件。
  触发关键词：[文件类型]、生成文件、创建文档、[英文关键词]。
  即使用户没有明确说"生成文件"，只要需要输出[文件类型]格式的内容，都应使用此技能。
compatibility:
  dependencies: [[对应库]]
```

**智能推荐逻辑：**
- 检测文件类型关键词（word/pdf/excel/ppt）
- 根据具体文件类型推荐对应依赖库
- 自动生成针对性的执行步骤

**执行步骤模板：**
1. 读取用户需求，确认文件类型和内容结构
2. 加载对应的模板文件（如有）
3. 使用脚本生成文件内容
4. 校验文件格式是否正确
5. 保存到输出目录并提供下载链接

**常见边界条件：**
- 文件大小建议不超过 50MB
- 不支持加密或受保护的文件
- 图片嵌入需确保格式为 PNG 或 JPG

**文件类型特定配置：**
```python
file_specific_configs = {
    'word': {
        'dependencies': ['python-docx'],
        'template_vars': ['{document_type}', '{content_structure}'],
        'keywords': ['word文档', 'docx', '报告', '合同']
    },
    'pdf': {
        'dependencies': ['reportlab', 'pdfplumber'],
        'template_vars': ['{page_layout}', '{content_type}'],
        'keywords': ['pdf', 'PDF文档', '电子书']
    },
    'excel': {
        'dependencies': ['openpyxl', 'pandas'],
        'template_vars': ['{sheet_structure}', '{data_format}'],
        'keywords': ['excel', '表格', 'xlsx', '数据表']
    }
}
```

---

## 模板 2：数据分析类（增强版）

适用场景：处理数据、生成统计报告、可视化。

```yaml
name: data-analyst
description: |
  当用户需要分析数据、生成图表、处理 CSV/Excel 文件时使用此技能。
  触发场景：数据统计、趋势分析、数据清洗、可视化报告。
  触发关键词：数据分析、统计、图表、可视化、CSV、Excel、数据处理。
compatibility:
  dependencies: [pandas, matplotlib, openpyxl, seaborn]
```

**智能推荐逻辑：**
- 识别数据格式（CSV/Excel/JSON）
- 检测分析类型（统计/可视化/清洗）
- 根据数据量推荐处理策略

**执行步骤模板：**
1. 加载数据文件，检查数据结构和质量
2. 清洗数据（处理缺失值、异常值）
3. 执行描述性统计分析
4. 生成可视化图表
5. 撰写分析摘要，输出报告

**常见边界条件：**
- 数据行数超过 10 万行时提示用户可能需要较长时间
- 不支持实时数据流，仅支持静态文件
- 图表中文字需确保字体支持中文显示

**分析类型特定配置：**
```python
analysis_types = {
    'descriptive': {
        'focus': '描述性统计',
        'charts': ['histogram', 'box_plot', 'summary_table'],
        'keywords': ['统计', '描述', '概况']
    },
    'correlation': {
        'focus': '相关性分析',
        'charts': ['scatter_plot', 'correlation_matrix', 'heatmap'],
        'keywords': ['相关性', '关系', '关联']
    },
    'trend': {
        'focus': '趋势分析',
        'charts': ['line_chart', 'time_series', 'moving_average'],
        'keywords': ['趋势', '时间序列', '变化']
    }
}
```

---

## 模板 3：代码辅助类（增强版）

适用场景：代码生成、审查、调试、重构。

```yaml
name: code-assistant
description: |
  当用户需要代码审查、调试、重构或生成代码时使用此技能。
  触发场景：看看这段代码有没有问题、帮我优化、帮我写一个函数、代码跑不通。
  触发关键词：代码审查、调试、重构、code review、帮我写代码、bug。
```

**智能推荐逻辑：**
- 识别编程语言（Python/JavaScript/Java等）
- 检测任务类型（生成/审查/调试/重构）
- 根据代码复杂度推荐处理方式

**执行步骤模板：**
1. 阅读并理解代码逻辑和用户目标
2. 识别问题或改进点（性能、可读性、安全性）
3. 起草修改方案
4. 生成改进后的代码
5. 解释变更原因，列出改动清单

**常见边界条件：**
- 代码超过 500 行时建议分模块处理
- 不执行用户的代码，只分析和生成
- 保持原有代码风格和约定

**语言特定配置：**
```python
language_configs = {
    'python': {
        'focus_areas': ['PEP8规范', '类型提示', '异常处理'],
        'tools': ['black', 'mypy', 'pylint'],
        'keywords': ['python', 'py', '脚本']
    },
    'javascript': {
        'focus_areas': ['ES6+语法', '异步处理', '模块化'],
        'tools': ['eslint', 'prettier', 'babel'],
        'keywords': ['javascript', 'js', 'node', '前端']
    },
    'java': {
        'focus_areas': ['设计模式', '异常处理', '性能优化'],
        'tools': ['checkstyle', 'spotbugs'],
        'keywords': ['java', 'spring', '企业级']
    }
}
```

---

## 模板 4：搜索研究类（增强版）

适用场景：网络搜索、信息整理、生成研究报告。

```yaml
name: deep-researcher
description: |
  当用户需要深度研究某个话题、对比信息或生成调研报告时使用此技能。
  触发场景：帮我了解、调研、找最新资料、对比分析、写一份报告。
  触发关键词：研究、调研、搜索、报告、对比、最新、了解一下。
```

**智能推荐逻辑：**
- 识别研究领域（技术/市场/竞品等）
- 检测研究深度（概览/深入/对比）
- 根据时效性要求调整搜索策略

**执行步骤模板：**
1. 分解研究问题，确定搜索维度
2. 执行多角度网络搜索
3. 筛选高质量信息源，过滤低质内容
4. 综合分析，识别共识与分歧
5. 撰写结构化报告，附来源列表

**常见边界条件：**
- 时效性强的信息以最近 6 个月内的来源为准
- 涉及医疗/法律建议需加免责声明
- 优先选择权威来源和学术资料

**研究领域特定配置：**
```python
research_domains = {
    'technology': {
        'sources': ['GitHub', 'Stack Overflow', '技术博客', '学术论文'],
        'keywords': ['技术', '开发', '编程', '架构'],
        'time_sensitivity': 'high'
    },
    'market': {
        'sources': ['行业报告', '新闻资讯', '公司官网', '财报'],
        'keywords': ['市场', '行业', '竞品', '趋势'],
        'time_sensitivity': 'medium'
    },
    'academic': {
        'sources': ['学术期刊', '研究论文', '大学网站', '实验室'],
        'keywords': ['学术', '研究', '论文', '理论'],
        'time_sensitivity': 'low'
    }
}
```

---

## 模板 5：流程自动化类（增强版）

适用场景：执行多步骤任务、批量操作、工作流自动化。

```yaml
name: workflow-automator
description: |
  当用户需要自动执行多步骤任务、批量处理或自动化工作流时使用此技能。
  触发场景：批量处理文件、自动生成多个输出、执行重复性任务。
  触发关键词：自动化、批量、工作流、自动执行、流程、pipeline。
compatibility:
  dependencies: [bash]
```

**智能推荐逻辑：**
- 识别任务类型（文件处理/数据处理/系统操作）
- 检测批量规模（单个/小批量/大批量）
- 根据风险等级推荐安全措施

**执行步骤模板：**
1. 理解工作流程的输入、步骤和预期输出
2. 拆分任务为可执行的子步骤
3. 逐步执行，每步确认结果
4. 处理异常情况，提供失败回滚方案
5. 汇总执行结果，输出操作日志

**常见边界条件：**
- 每步执行前确认，避免不可逆操作
- 批量任务超过 50 个时建议先用小样本测试
- 提供详细的执行日志和错误信息

**自动化类型配置：**
```python
automation_types = {
    'file_processing': {
        'risks': ['文件覆盖', '权限问题', '路径错误'],
        'safety_measures': ['备份原文件', '权限检查', '路径验证'],
        'keywords': ['文件处理', '批量操作', '格式转换']
    },
    'data_processing': {
        'risks': ['数据丢失', '格式错误', '内存溢出'],
        'safety_measures': ['数据备份', '格式验证', '分批处理'],
        'keywords': ['数据处理', '数据清洗', '格式转换']
    },
    'system_operations': {
        'risks': ['系统损坏', '权限滥用', '服务中断'],
        'safety_measures': ['权限最小化', '操作确认', '回滚方案'],
        'keywords': ['系统操作', '服务管理', '配置修改']
    }
}
```

---

## 智能名称推荐系统

### 命名规则
- 小写字母 + 连字符（如 `pdf-creator`）
- 体现核心功能（如 `data-analyst`）
- 简洁易记（如 `code-helper`）

### 推荐算法
1. **基于功能**：从技能类型提取核心词
2. **基于对象**：从处理对象提取关键词
3. **基于动作**：从执行动作提取动词
4. **置信度评分**：综合多个因素计算推荐置信度

### 名称模式库
```python
name_patterns = {
    'file': ['{type}-creator', '{type}-generator', 'doc-{type}', '{type}-maker'],
    'data': ['data-{type}', '{type}-analyzer', 'insight-{type}', '{type}-viz'],
    'code': ['{lang}-helper', 'code-{type}', '{lang}-fixer', '{lang}-writer'],
    'research': ['{topic}-research', 'deep-{topic}', '{topic}-analysis', 'smart-{topic}'],
    'automation': ['auto-{task}', '{task}-flow', 'batch-{task}', '{task}-bot']
}
```

---

## 通用 README 模板（增强版）

```markdown
# [技能名称]

[一句话描述这个技能做什么]

## 安装

将此文件夹放到项目的 `.claude/skills/` 目录下：

```
你的项目/
└── .claude/
    └── skills/
        └── [skill-name]/
```

## 触发方式

在 Claude Code 中说：
- "[触发示例1]"
- "[触发示例2]"
- "[触发示例3]"

**智能触发**：系统会根据您的意图自动识别并调用此技能，无需明确提及技能名称。

## 文件结构

```
[skill-name]/
├── SKILL.md          核心技能描述
├── README.md         本文件
[根据实际情况列出其他文件]
```

## 依赖

[无 / 列出依赖及安装命令]

```bash
pip install [依赖包列表]
```

## 使用技巧

- **最佳输入**：[描述最佳输入格式]
- **常见场景**：[列出典型使用场景]
- **注意事项**：[重要提醒]

---

*由 Skill Generator 智能生成*
```
