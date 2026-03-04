#!/usr/bin/env python3
"""
skill_preview.py

技能预览和实时编辑模块。
提供技能信息的实时预览、编辑和格式化功能。
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class SkillPreview:
    """技能预览数据"""
    name: str
    description: str
    summary: str
    dependencies: List[str]
    input_desc: str
    output_desc: str
    steps: List[str]
    notes: List[str]
    file_structure: Dict[str, Any]
    completion_rate: float


@dataclass
class EditOperation:
    """编辑操作"""
    field: str
    operation: str  # 'add', 'remove', 'replace', 'insert'
    value: Any
    position: Optional[int] = None


class SkillPreviewer:
    """技能预览器"""
    
    def __init__(self):
        self.preview_cache = {}
        self.edit_history = []
    
    def generate_preview(self, skill_data: Dict[str, Any]) -> SkillPreview:
        """
        生成技能预览
        
        Args:
            skill_data: 技能数据
            
        Returns:
            SkillPreview: 预览数据
        """
        # 计算完成率
        completion_rate = self._calculate_completion_rate(skill_data)
        
        # 生成文件结构预览
        file_structure = self._generate_file_structure_preview(skill_data)
        
        # 提取基本信息
        preview = SkillPreview(
            name=skill_data.get('name', '未命名技能'),
            description=skill_data.get('description', ''),
            summary=skill_data.get('summary', ''),
            dependencies=skill_data.get('dependencies', []),
            input_desc=skill_data.get('input_desc', ''),
            output_desc=skill_data.get('output_desc', ''),
            steps=skill_data.get('steps', []),
            notes=skill_data.get('notes', []),
            file_structure=file_structure,
            completion_rate=completion_rate
        )
        
        # 缓存预览
        self.preview_cache[skill_data.get('name', 'unnamed')] = preview
        
        return preview
    
    def format_preview_display(self, preview: SkillPreview) -> str:
        """
        格式化预览显示
        
        Args:
            preview: 预览数据
            
        Returns:
            str: 格式化的预览文本
        """
        display = []
        
        # 标题和进度
        progress_bar = self._generate_progress_bar(preview.completion_rate)
        display.append(f"📋 **{preview.name}** - 完成度 {preview.completion_rate:.1f}%")
        display.append(f"{progress_bar}")
        display.append("")
        
        # 基本信息
        if preview.summary:
            display.append(f"📝 **简介**: {preview.summary}")
            display.append("")
        
        if preview.description:
            display.append("🎯 **触发描述**:")
            display.append(f"```")
            display.append(preview.description)
            display.append(f"```")
            display.append("")
        
        # 输入输出
        display.append("🔄 **输入输出**:")
        display.append(f"- **输入**: {preview.input_desc}")
        display.append(f"- **输出**: {preview.output_desc}")
        display.append("")
        
        # 依赖
        if preview.dependencies:
            display.append("📦 **依赖库**:")
            for dep in preview.dependencies:
                display.append(f"- `{dep}`")
            display.append("")
        
        # 执行步骤
        if preview.steps:
            display.append("⚡ **执行步骤**:")
            for i, step in enumerate(preview.steps, 1):
                display.append(f"{i}. {step}")
            display.append("")
        
        # 注意事项
        if preview.notes:
            display.append("⚠️ **注意事项**:")
            for note in preview.notes:
                display.append(f"- {note}")
            display.append("")
        
        # 文件结构
        display.append("📁 **文件结构**:")
        display.append(self._format_file_structure(preview.file_structure))
        display.append("")
        
        # 缺失字段提示
        missing_fields = self._get_missing_fields(preview)
        if missing_fields:
            display.append("🔍 **待完善**:")
            for field in missing_fields:
                display.append(f"- {field}")
            display.append("")
        
        return "\n".join(display)
    
    def apply_edit(self, skill_data: Dict[str, Any], operation: EditOperation) -> Tuple[Dict[str, Any], bool]:
        """
        应用编辑操作
        
        Args:
            skill_data: 原始技能数据
            operation: 编辑操作
            
        Returns:
            Tuple[Dict[str, Any], bool]: (更新后的数据, 是否成功)
        """
        try:
            # 记录编辑历史
            self.edit_history.append({
                'timestamp': self._get_timestamp(),
                'operation': operation,
                'old_data': skill_data.copy()
            })
            
            # 应用编辑
            updated_data = skill_data.copy()
            
            if operation.operation == 'replace':
                updated_data[operation.field] = operation.value
            elif operation.operation == 'add':
                if isinstance(operation.value, list) and operation.field in updated_data:
                    updated_data[operation.field].extend(operation.value)
                else:
                    updated_data[operation.field] = operation.value
            elif operation.operation == 'remove':
                if operation.field in updated_data:
                    if isinstance(operation.value, list):
                        for item in operation.value:
                            if item in updated_data[operation.field]:
                                updated_data[operation.field].remove(item)
                    elif operation.value in updated_data[operation.field]:
                        updated_data[operation.field].remove(operation.value)
            elif operation.operation == 'insert':
                if operation.field in updated_data and isinstance(updated_data[operation.field], list):
                    if operation.position is not None:
                        updated_data[operation.field].insert(operation.position, operation.value)
                    else:
                        updated_data[operation.field].append(operation.value)
            
            return updated_data, True
            
        except Exception as e:
            print(f"编辑失败: {e}")
            return skill_data, False
    
    def generate_skill_files_preview(self, skill_data: Dict[str, Any]) -> Dict[str, str]:
        """
        生成技能文件预览
        
        Args:
            skill_data: 技能数据
            
        Returns:
            Dict[str, str]: 文件名到内容的映射
        """
        files = {}
        
        # SKILL.md
        files['SKILL.md'] = self._generate_skill_md_content(skill_data)
        
        # README.md
        files['README.md'] = self._generate_readme_content(skill_data)
        
        # scripts/main.py (如果需要)
        if skill_data.get('has_scripts', False):
            files['scripts/main.py'] = self._generate_main_script_content(skill_data)
        
        # references/guide.md (如果需要)
        if skill_data.get('has_refs', False):
            files['references/guide.md'] = self._generate_reference_content(skill_data)
        
        return files
    
    def validate_skill_data(self, skill_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证技能数据
        
        Args:
            skill_data: 技能数据
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误列表)
        """
        errors = []
        
        # 必填字段检查
        required_fields = ['name', 'description']
        for field in required_fields:
            if not skill_data.get(field):
                errors.append(f"缺少必填字段: {field}")
        
        # 名称格式检查
        name = skill_data.get('name', '')
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append("技能名称只能包含小写字母、数字和连字符")
        
        # 描述长度检查
        description = skill_data.get('description', '')
        if len(description) < 50:
            errors.append("触发描述太短，建议至少50个字符")
        elif len(description) > 300:
            errors.append("触发描述太长，建议控制在300字符以内")
        
        # 步骤检查
        steps = skill_data.get('steps', [])
        if not steps:
            errors.append("至少需要一个执行步骤")
        elif len(steps) > 10:
            errors.append("执行步骤过多，建议控制在10步以内")
        
        return len(errors) == 0, errors
    
    def get_edit_suggestions(self, skill_data: Dict[str, Any]) -> List[str]:
        """
        获取编辑建议
        
        Args:
            skill_data: 技能数据
            
        Returns:
            List[str]: 建议列表
        """
        suggestions = []
        
        # 基于完成度给出建议
        completion_rate = self._calculate_completion_rate(skill_data)
        
        if completion_rate < 0.5:
            suggestions.append("建议先完善基本信息（名称、描述）")
        
        if not skill_data.get('summary'):
            suggestions.append("添加技能简介，让用户快速了解功能")
        
        if not skill_data.get('dependencies'):
            suggestions.append("考虑是否需要添加依赖库")
        
        if not skill_data.get('notes'):
            suggestions.append("添加注意事项，说明使用限制")
        
        if len(skill_data.get('steps', [])) < 3:
            suggestions.append("执行步骤可以更详细一些")
        
        # 检查描述质量
        description = skill_data.get('description', '')
        if '关键词' not in description:
            suggestions.append("在描述中明确说明触发关键词")
        
        return suggestions
    
    # 私有辅助方法
    def _calculate_completion_rate(self, skill_data: Dict[str, Any]) -> float:
        """计算完成率"""
        total_fields = 8  # name, description, summary, dependencies, input_desc, output_desc, steps, notes
        completed_fields = 0
        
        field_checks = {
            'name': lambda x: bool(x and x.strip()),
            'description': lambda x: bool(x and len(x.strip()) >= 50),
            'summary': lambda x: bool(x and x.strip()),
            'dependencies': lambda x: isinstance(x, list) and len(x) > 0,
            'input_desc': lambda x: bool(x and x.strip()),
            'output_desc': lambda x: bool(x and x.strip()),
            'steps': lambda x: isinstance(x, list) and len(x) > 0,
            'notes': lambda x: isinstance(x, list) and len(x) > 0
        }
        
        for field, check in field_checks.items():
            if check(skill_data.get(field)):
                completed_fields += 1
        
        return completed_fields / total_fields
    
    def _generate_file_structure_preview(self, skill_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成文件结构预览"""
        structure = {
            'SKILL.md': '✅ 核心技能描述',
            'README.md': '✅ 使用说明文档'
        }
        
        if skill_data.get('has_scripts'):
            structure['scripts/'] = {
                '__init__.py': '📄 Python包初始化',
                'main.py': '📄 主执行脚本'
            }
        
        if skill_data.get('has_refs'):
            structure['references/'] = {
                'guide.md': '📄 参考指南'
            }
        
        if skill_data.get('has_assets'):
            structure['assets/'] = '📁 模板和素材文件'
        
        if skill_data.get('has_evals'):
            structure['evals/'] = {
                'evals.json': '📄 测试用例',
                'files/': '📁 测试文件'
            }
        
        return structure
    
    def _format_file_structure(self, structure: Dict[str, Any], indent: int = 0) -> str:
        """格式化文件结构显示"""
        lines = []
        prefix = "  " * indent
        
        for name, content in structure.items():
            if isinstance(content, dict):
                lines.append(f"{prefix}📁 {name}/")
                lines.append(self._format_file_structure(content, indent + 1))
            else:
                lines.append(f"{prefix}📄 {name} - {content}")
        
        return "\n".join(lines)
    
    def _generate_progress_bar(self, rate: float, width: int = 20) -> str:
        """生成进度条"""
        filled = int(rate * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _get_missing_fields(self, preview: SkillPreview) -> List[str]:
        """获取缺失字段"""
        missing = []
        
        if not preview.summary:
            missing.append("技能简介")
        if not preview.dependencies:
            missing.append("依赖库")
        if not preview.notes:
            missing.append("注意事项")
        
        return missing
    
    def _generate_skill_md_content(self, skill_data: Dict[str, Any]) -> str:
        """生成 SKILL.md 内容"""
        name = skill_data.get('name', 'my-skill')
        description = skill_data.get('description', '')
        summary = skill_data.get('summary', '')
        deps = skill_data.get('dependencies', [])
        input_desc = skill_data.get('input_desc', '')
        output_desc = skill_data.get('output_desc', '')
        steps = skill_data.get('steps', [])
        notes = skill_data.get('notes', [])
        
        lines = ["---", f"name: {name}", "description: |"]
        for line in description.strip().split("\n"):
            lines.append(f"  {line}")
        
        if deps:
            lines.append("compatibility:")
            lines.append(f"  dependencies: [{', '.join(deps)}]")
        
        lines += ["---", "", f"# {name}", ""]
        
        if summary:
            lines += [summary, ""]
        
        lines += ["## 输入", "", input_desc, "", "## 输出", "", output_desc, "", "## 执行步骤", ""]
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")
        
        if notes:
            lines += ["", "## 注意事项", ""]
            for note in notes:
                lines.append(f"- {note}")
        
        return "\n".join(lines) + "\n"
    
    def _generate_readme_content(self, skill_data: Dict[str, Any]) -> str:
        """生成 README.md 内容"""
        name = skill_data.get('name', 'my-skill')
        summary = skill_data.get('summary', '')
        deps = skill_data.get('dependencies', [])
        
        return f"""# {name}

{summary or "（请填写技能简介）"}

## 安装

将此文件夹放到项目的 `.claude/skills/` 目录下：

```
你的项目/
└── .claude/
    └── skills/
        └── {name}/
```

## 使用方式

在 Claude Code 中，直接描述你的需求，Claude 会自动识别并调用此技能。

## 依赖安装

{"无特殊依赖" if not deps else "```bash" + chr(10) + f"pip install {' '.join(deps)}" + chr(10) + "```"}

## 文件说明

- `SKILL.md` — 核心技能描述，Claude 的行为指南
- `README.md` — 本文件，面向使用者的说明

---
*由 Skill Generator 生成*
"""
    
    def _generate_main_script_content(self, skill_data: Dict[str, Any]) -> str:
        """生成主脚本内容"""
        name = skill_data.get('name', 'my-skill')
        return f'''#!/usr/bin/env python3
"""
{name} - 主执行脚本

用途：{skill_data.get('summary', '执行特定任务')}
输入：{skill_data.get('input_desc', '用户输入')}
输出：{skill_data.get('output_desc', '处理结果')}

用法：
  python scripts/main.py --input <输入文件> --output <输出目录>
"""

import argparse
import sys
from pathlib import Path


def main(input_path: str, output_dir: str) -> dict:
    """
    主执行函数。
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录路径
    
    Returns:
        dict: {{"success": bool, "output": str, "message": str}}
    """
    # TODO: 实现核心逻辑
    input_file = Path(input_path)
    output_path = Path(output_dir)
    
    if not input_file.exists():
        return {{"success": False, "message": f"文件不存在: {{input_path}}"}}
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 示例：处理逻辑
    print(f"处理文件: {{input_file.name}}")
    
    return {{
        "success": True,
        "output": str(output_path),
        "message": "处理完成"
    }}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="{name} 执行脚本")
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--output", default="./output", help="输出目录路径")
    args = parser.parse_args()

    result = main(args.input, args.output)
    
    if result["success"]:
        print(f"✓ {{result['message']}}")
        print(f"  输出目录: {{result['output']}}")
    else:
        print(f"✗ 错误: {{result['message']}}", file=sys.stderr)
        sys.exit(1)
'''
    
    def _generate_reference_content(self, skill_data: Dict[str, Any]) -> str:
        """生成参考文档内容"""
        name = skill_data.get('name', 'my-skill')
        return f"""# {name} — 参考指南

本文档包含执行此技能时需要了解的背景知识。
SKILL.md 正文会在需要时引导 Claude 读取本文件。

---

## 目录

1. [核心概念](#核心概念)
2. [常见场景](#常见场景)
3. [已知问题与解决方案](#已知问题与解决方案)

---

## 核心概念

[在这里填写技能相关的背景知识、技术细节、最佳实践等]

---

## 常见场景

### 场景一：[描述场景]

**输入示例：**
```
[示例输入]
```

**期望输出：**
```
[示例输出]
```

---

## 已知问题与解决方案

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| [问题描述] | [原因] | [解决方法] |

"""
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局预览器实例
skill_previewer = SkillPreviewer()
