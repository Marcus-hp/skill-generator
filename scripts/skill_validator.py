#!/usr/bin/env python3
"""
skill_validator.py

技能配置验证模块。
使用 JSON Schema 进行严格的数据验证，确保技能配置的正确性和一致性。
"""

import json
import jsonschema
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]


class SkillValidator:
    """技能验证器"""
    
    def __init__(self):
        self.schema = self._load_skill_schema()
        self.custom_validators = self._init_custom_validators()
    
    def _load_skill_schema(self) -> Dict[str, Any]:
        """加载技能配置的 JSON Schema"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Skill Configuration Schema",
            "description": "Schema for validating Claude Agent Skill configurations",
            "required": ["name", "description"],
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[a-z0-9-]+$",
                    "minLength": 3,
                    "maxLength": 50,
                    "title": "Skill Name",
                    "description": "Lowercase letters, numbers, and hyphens only"
                },
                "description": {
                    "type": "string",
                    "minLength": 50,
                    "maxLength": 300,
                    "title": "Trigger Description",
                    "description": "Description that determines when Claude should use this skill"
                },
                "summary": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 200,
                    "title": "Skill Summary",
                    "description": "Brief description of what this skill does"
                },
                "dependencies": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "pattern": "^[a-zA-Z0-9._-]+$"
                    },
                    "uniqueItems": True,
                    "title": "Dependencies",
                    "description": "List of required Python packages or system tools"
                },
                "platforms": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["claude-code", "claude-ai", "claude-desktop"]
                    },
                    "uniqueItems": True,
                    "default": ["claude-code", "claude-ai"],
                    "title": "Supported Platforms"
                },
                "input_desc": {
                    "type": "string",
                    "minLength": 5,
                    "maxLength": 200,
                    "title": "Input Description",
                    "description": "Description of what users typically provide"
                },
                "output_desc": {
                    "type": "string",
                    "minLength": 5,
                    "maxLength": 200,
                    "title": "Output Description",
                    "description": "Description of what the skill delivers"
                },
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 5,
                        "maxLength": 200
                    },
                    "minItems": 1,
                    "maxItems": 10,
                    "title": "Execution Steps",
                    "description": "Step-by-step instructions for Claude"
                },
                "notes": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 5,
                        "maxLength": 200
                    },
                    "maxItems": 10,
                    "title": "Notes",
                    "description": "Important notes and limitations"
                },
                "has_scripts": {
                    "type": "boolean",
                    "default": False,
                    "title": "Has Scripts Directory"
                },
                "has_refs": {
                    "type": "boolean", 
                    "default": False,
                    "title": "Has References Directory"
                },
                "has_assets": {
                    "type": "boolean",
                    "default": False,
                    "title": "Has Assets Directory"
                },
                "has_evals": {
                    "type": "boolean",
                    "default": False,
                    "title": "Has Evals Directory"
                },
                "version": {
                    "type": "string",
                    "pattern": "^v\\d+\\.\\d+\\.\\d+$",
                    "default": "v1.0.0",
                    "title": "Version",
                    "description": "Semantic version (e.g., v1.0.0)"
                },
                "author": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 50,
                    "title": "Author",
                    "description": "Skill author name"
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "pattern": "^[a-zA-Z0-9_-]+$"
                    },
                    "uniqueItems": True,
                    "maxItems": 5,
                    "title": "Tags",
                    "description": "Tags for categorizing the skill"
                }
            },
            "additionalProperties": False
        }
    
    def _init_custom_validators(self) -> Dict[str, callable]:
        """初始化自定义验证器"""
        return {
            'description_quality': self._validate_description_quality,
            'name_availability': self._validate_name_availability,
            'dependency_compatibility': self._validate_dependency_compatibility,
            'step_logic': self._validate_step_logic,
            'content_consistency': self._validate_content_consistency
        }
    
    def validate_skill_config(self, skill_data: Dict[str, Any], 
                            skills_dir: str = ".claude/skills") -> ValidationResult:
        """
        验证技能配置
        
        Args:
            skill_data: 技能配置数据
            skills_dir: 技能目录路径
            
        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        warnings = []
        suggestions = []
        
        # JSON Schema 验证
        try:
            jsonschema.validate(skill_data, self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
        except jsonschema.SchemaError as e:
            errors.append(f"Schema error: {e.message}")
        
        # 自定义验证
        for validator_name, validator_func in self.custom_validators.items():
            try:
                validator_errors, validator_warnings, validator_suggestions = validator_func(
                    skill_data, skills_dir
                )
                errors.extend(validator_errors)
                warnings.extend(validator_warnings)
                suggestions.extend(validator_suggestions)
            except Exception as e:
                warnings.append(f"Custom validator {validator_name} failed: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def validate_skill_files(self, skill_dir: Path) -> ValidationResult:
        """
        验证技能文件结构
        
        Args:
            skill_dir: 技能目录路径
            
        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        warnings = []
        suggestions = []
        
        # 检查必需文件
        required_files = ["SKILL.md", "README.md"]
        for file_name in required_files:
            file_path = skill_dir / file_name
            if not file_path.exists():
                errors.append(f"Missing required file: {file_name}")
            elif file_path.stat().st_size == 0:
                errors.append(f"Required file is empty: {file_name}")
        
        # 检查 SKILL.md 格式
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            md_errors, md_warnings = self._validate_skill_md_format(skill_md)
            errors.extend(md_errors)
            warnings.extend(md_warnings)
        
        # 检查目录结构一致性
        structure_errors, structure_warnings = self._validate_directory_structure(skill_dir)
        errors.extend(structure_errors)
        warnings.extend(structure_warnings)
        
        # 检查脚本文件
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.exists():
            script_errors, script_warnings = self._validate_scripts(scripts_dir)
            errors.extend(script_errors)
            warnings.extend(script_warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def generate_validation_report(self, result: ValidationResult, 
                                  skill_name: str = "Unknown") -> str:
        """
        生成验证报告
        
        Args:
            result: 验证结果
            skill_name: 技能名称
            
        Returns:
            str: 格式化的验证报告
        """
        report_lines = []
        
        # 标题
        status = "✅ 通过" if result.is_valid else "❌ 失败"
        report_lines.append(f"# {skill_name} 验证报告 - {status}")
        report_lines.append("")
        
        # 错误
        if result.errors:
            report_lines.append("## 🚨 错误 (必须修复)")
            for i, error in enumerate(result.errors, 1):
                report_lines.append(f"{i}. {error}")
            report_lines.append("")
        
        # 警告
        if result.warnings:
            report_lines.append("## ⚠️ 警告 (建议修复)")
            for i, warning in enumerate(result.warnings, 1):
                report_lines.append(f"{i}. {warning}")
            report_lines.append("")
        
        # 建议
        if result.suggestions:
            report_lines.append("## 💡 建议 (可选改进)")
            for i, suggestion in enumerate(result.suggestions, 1):
                report_lines.append(f"{i}. {suggestion}")
            report_lines.append("")
        
        # 总结
        if result.is_valid:
            report_lines.append("## ✅ 验证通过")
            report_lines.append("技能配置符合所有规范，可以正常使用。")
        else:
            report_lines.append("## ❌ 验证失败")
            report_lines.append(f"发现 {len(result.errors)} 个错误，请修复后重新验证。")
        
        return "\n".join(report_lines)
    
    # 自定义验证器
    def _validate_description_quality(self, skill_data: Dict[str, Any], 
                                    skills_dir: str) -> Tuple[List[str], List[str], List[str]]:
        """验证描述质量"""
        errors = []
        warnings = []
        suggestions = []
        
        description = skill_data.get('description', '')
        
        # 检查关键词
        required_keywords = ['触发', '关键词', '场景']
        missing_keywords = [kw for kw in required_keywords if kw not in description]
        if missing_keywords:
            warnings.append(f"描述中缺少关键词: {', '.join(missing_keywords)}")
        
        # 检查英文关键词
        has_english = any(char.isascii() and char.isalpha() for char in description)
        if not has_english:
            suggestions.append("建议在描述中添加英文关键词，提高触发准确性")
        
        # 检查场景描述
        if '包括' not in description and '例如' not in description:
            suggestions.append("建议添加具体的使用场景示例")
        
        return errors, warnings, suggestions
    
    def _validate_name_availability(self, skill_data: Dict[str, Any], 
                                  skills_dir: str) -> Tuple[List[str], List[str], List[str]]:
        """验证名称可用性"""
        errors = []
        warnings = []
        suggestions = []
        
        name = skill_data.get('name', '')
        skills_path = Path(skills_dir)
        
        # 检查名称冲突
        if skills_path.exists():
            existing_skill = skills_path / name
            if existing_skill.exists():
                errors.append(f"技能名称已存在: {name}")
        
        # 检查名称质量
        if name.count('-') > 3:
            warnings.append("技能名称连字符过多，可能影响可读性")
        
        if any(part.isdigit() for part in name.split('-')):
            suggestions.append("建议使用更具描述性的名称，避免纯数字部分")
        
        return errors, warnings, suggestions
    
    def _validate_dependency_compatibility(self, skill_data: Dict[str, Any], 
                                        skills_dir: str) -> Tuple[List[str], List[str], List[str]]:
        """验证依赖兼容性"""
        errors = []
        warnings = []
        suggestions = []
        
        dependencies = skill_data.get('dependencies', [])
        
        # 检查常见依赖的版本兼容性
        known_issues = {
            'tensorflow': ['建议指定版本，避免兼容性问题'],
            'torch': ['PyTorch 需要考虑 CUDA 版本'],
            'opencv-python': ['可能与 opencv-contrib-python 冲突']
        }
        
        for dep in dependencies:
            dep_name = dep.split('==')[0].split('>=')[0].split('<=')[0]
            if dep_name in known_issues:
                warnings.extend([f"{dep}: {issue}" for issue in known_issues[dep_name]])
        
        # 检查依赖数量
        if len(dependencies) > 10:
            warnings.append("依赖过多，可能影响安装速度和兼容性")
        
        return errors, warnings, suggestions
    
    def _validate_step_logic(self, skill_data: Dict[str, Any], 
                           skills_dir: str) -> Tuple[List[str], List[str], List[str]]:
        """验证步骤逻辑"""
        errors = []
        warnings = []
        suggestions = []
        
        steps = skill_data.get('steps', [])
        
        # 检查步骤完整性
        if len(steps) < 2:
            suggestions.append("建议至少包含2个步骤，描述完整的执行流程")
        
        # 检查步骤动词
        action_words = ['读取', '分析', '处理', '生成', '保存', '验证', '执行']
        has_actions = any(any(word in step for word in action_words) for step in steps)
        if not has_actions:
            suggestions.append("建议在步骤中使用明确的动作词汇")
        
        # 检查步骤顺序逻辑
        if len(steps) >= 3:
            # 检查是否有输入处理步骤
            has_input = any('输入' in step or '读取' in step for step in steps[:2])
            if not has_input:
                warnings.append("建议在前几个步骤中包含输入处理")
            
            # 检查是否有输出步骤
            has_output = any('输出' in step or '保存' in step or '生成' in step for step in steps[-2:])
            if not has_output:
                warnings.append("建议在最后步骤中包含输出处理")
        
        return errors, warnings, suggestions
    
    def _validate_content_consistency(self, skill_data: Dict[str, Any], 
                                    skills_dir: str) -> Tuple[List[str], List[str], List[str]]:
        """验证内容一致性"""
        errors = []
        warnings = []
        suggestions = []
        
        description = skill_data.get('description', '')
        summary = skill_data.get('summary', '')
        input_desc = skill_data.get('input_desc', '')
        output_desc = skill_data.get('output_desc', '')
        
        # 检查描述和摘要的一致性
        if summary and description:
            # 提取关键词
            desc_keywords = set(description.replace('，', ' ').replace('。', ' ').split())
            sum_keywords = set(summary.replace('，', ' ').replace('。', ' ').split())
            
            common_keywords = desc_keywords & sum_keywords
            if len(common_keywords) < 2:
                warnings.append("摘要和描述的关键词差异较大，建议保持一致性")
        
        # 检查输入输出的逻辑性
        if input_desc and output_desc:
            if '文件' in input_desc and '文件' not in output_desc:
                if '数据' not in output_desc and '结果' not in output_desc:
                    suggestions.append("输入是文件，输出描述应该体现文件处理结果")
        
        return errors, warnings, suggestions
    
    def _validate_skill_md_format(self, skill_md: Path) -> Tuple[List[str], List[str]]:
        """验证 SKILL.md 格式"""
        errors = []
        warnings = []
        
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查 frontmatter
            if not content.startswith('---'):
                errors.append("SKILL.md 必须以 YAML frontmatter 开头")
            else:
                parts = content.split('---')
                if len(parts) < 3:
                    errors.append("YAML frontmatter 格式不正确")
                else:
                    frontmatter = parts[1]
                    if 'name:' not in frontmatter:
                        errors.append("frontmatter 缺少 name 字段")
                    if 'description:' not in frontmatter:
                        errors.append("frontmatter 缺少 description 字段")
            
            # 检查必需的章节
            required_sections = ['输入', '输出', '执行步骤']
            for section in required_sections:
                if f"## {section}" not in content:
                    errors.append(f"缺少必需章节: {section}")
            
        except Exception as e:
            errors.append(f"读取 SKILL.md 失败: {str(e)}")
        
        return errors, warnings
    
    def _validate_directory_structure(self, skill_dir: Path) -> Tuple[List[str], List[str]]:
        """验证目录结构"""
        errors = []
        warnings = []
        
        # 检查 SKILL.md 中的目录声明
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查声明的目录是否存在
            if 'scripts/' in content and not (skill_dir / 'scripts').exists():
                warnings.append("SKILL.md 引用了 scripts/ 目录但目录不存在")
            
            if 'references/' in content and not (skill_dir / 'references').exists():
                warnings.append("SKILL.md 引用了 references/ 目录但目录不存在")
        
        return errors, warnings
    
    def _validate_scripts(self, scripts_dir: Path) -> Tuple[List[str], List[str]]:
        """验证脚本文件"""
        errors = []
        warnings = []
        
        # 检查 __init__.py
        init_py = scripts_dir / "__init__.py"
        if not init_py.exists():
            warnings.append("scripts/ 目录缺少 __init__.py 文件")
        
        # 检查 Python 脚本语法
        for py_file in scripts_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, str(py_file), 'exec')
            except SyntaxError as e:
                errors.append(f"脚本语法错误 {py_file.name}: {e}")
        
        return errors, warnings


# 全局验证器实例
skill_validator = SkillValidator()
