#!/usr/bin/env python3
"""
skill_updater.py

技能更新模块。
支持修改已有技能、版本管理、变更记录等功能。
"""

import json
import os
import shutil
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SkillChange:
    """技能变更记录"""
    timestamp: str
    change_type: str  # 'create', 'update', 'delete'
    field: str
    old_value: Any
    new_value: Any
    reason: str


@dataclass
class SkillVersion:
    """技能版本信息"""
    version: str
    timestamp: str
    changes: List[SkillChange]
    description: str
    skill_data: Dict[str, Any]


class SkillUpdater:
    """技能更新器"""
    
    def __init__(self, skills_dir: Optional[str] = None):
        if skills_dir is None:
            project_root = Path(os.environ.get("SKILL_DATA_DIR", "."))
            skills_dir = str(project_root / ".claude" / "skills")
        self.skills_dir = Path(skills_dir)
        self.backup_dir = self.skills_dir / ".backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.change_history: List[SkillChange] = []
    
    def list_existing_skills(self) -> List[Dict[str, Any]]:
        """
        列出所有已有技能
        
        Returns:
            List[Dict[str, Any]]: 技能信息列表
        """
        skills = []
        
        if not self.skills_dir.exists():
            return skills
        
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                skill_info = self._get_skill_info(skill_dir)
                if skill_info:
                    skills.append(skill_info)
        
        # 按修改时间排序
        skills.sort(key=lambda x: x.get('last_modified', 0), reverse=True)
        return skills
    
    def load_skill_for_editing(self, skill_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        加载技能用于编辑
        
        Args:
            skill_name: 技能名称
            
        Returns:
            Tuple[Optional[Dict[str, Any]], Optional[str]]: (技能数据, 错误信息)
        """
        skill_dir = self.skills_dir / skill_name
        
        if not skill_dir.exists():
            return None, f"技能不存在：{skill_name}"
        
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            return None, f"技能文件不存在：{skill_file}"
        
        try:
            # 解析 SKILL.md
            skill_data = self._parse_skill_file(skill_file)
            
            # 读取其他文件信息
            skill_data.update(self._read_additional_files(skill_dir))
            
            return skill_data, None
            
        except Exception as e:
            return None, f"加载技能失败：{str(e)}"
    
    def update_skill(self, skill_name: str, updates: Dict[str, Any], 
                    reason: str = "用户修改") -> Tuple[bool, Optional[str]]:
        """
        更新技能
        
        Args:
            skill_name: 技能名称
            updates: 更新内容
            reason: 更新原因
            
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        try:
            # 创建备份
            backup_success = self._create_backup(skill_name)
            if not backup_success:
                return False, "创建备份失败"
            
            # 加载当前技能数据
            current_data, error = self.load_skill_for_editing(skill_name)
            if error:
                return False, error
            
            # 记录变更
            changes = self._detect_changes(current_data, updates, reason)
            
            # 应用更新
            updated_data = current_data.copy()
            updated_data.update(updates)
            
            # 验证数据
            is_valid, validation_errors = self._validate_skill_data(updated_data)
            if not is_valid:
                return False, f"数据验证失败：{'; '.join(validation_errors)}"
            
            # 保存更新
            save_success = self._save_skill_updates(skill_name, updated_data)
            if not save_success:
                return False, "保存更新失败"
            
            # 记录变更历史
            self._record_changes(skill_name, changes)
            
            return True, None
            
        except Exception as e:
            return False, f"更新技能失败：{str(e)}"
    
    def rename_skill(self, old_name: str, new_name: str) -> Tuple[bool, Optional[str]]:
        """
        重命名技能
        
        Args:
            old_name: 旧名称
            new_name: 新名称
            
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        try:
            old_dir = self.skills_dir / old_name
            new_dir = self.skills_dir / new_name
            
            if not old_dir.exists():
                return False, f"技能不存在：{old_name}"
            
            if new_dir.exists():
                return False, f"目标名称已存在：{new_name}"
            
            # 验证新名称格式
            if not self._validate_skill_name(new_name):
                return False, "技能名称格式不正确"
            
            # 创建备份
            self._create_backup(old_name)
            
            # 重命名目录
            old_dir.rename(new_dir)
            
            # 更新文件内容中的名称
            self._update_skill_name_in_files(new_dir, new_name)
            
            return True, None
            
        except Exception as e:
            return False, f"重命名失败：{str(e)}"
    
    def delete_skill(self, skill_name: str, confirm: bool = False) -> Tuple[bool, Optional[str]]:
        """
        删除技能
        
        Args:
            skill_name: 技能名称
            confirm: 是否确认删除
            
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        if not confirm:
            return False, "需要确认删除操作"
        
        try:
            skill_dir = self.skills_dir / skill_name
            
            if not skill_dir.exists():
                return False, f"技能不存在：{skill_name}"
            
            # 创建最后备份
            self._create_backup(skill_name)
            
            # 删除目录
            shutil.rmtree(skill_dir)
            
            return True, None
            
        except Exception as e:
            return False, f"删除失败：{str(e)}"
    
    def get_skill_history(self, skill_name: str) -> List[SkillVersion]:
        """
        获取技能变更历史
        
        Args:
            skill_name: 技能名称
            
        Returns:
            List[SkillVersion]: 版本历史
        """
        history_file = self.backup_dir / f"{skill_name}_history.json"
        
        if not history_file.exists():
            return []
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            versions = []
            for version_data in data.get('versions', []):
                changes = [SkillChange(**change) for change in version_data.get('changes', [])]
                version = SkillVersion(
                    version=version_data['version'],
                    timestamp=version_data['timestamp'],
                    changes=changes,
                    description=version_data['description'],
                    skill_data=version_data['skill_data']
                )
                versions.append(version)
            
            return versions
            
        except Exception as e:
            print(f"读取历史记录失败：{e}")
            return []
    
    def restore_skill_version(self, skill_name: str, version: str) -> Tuple[bool, Optional[str]]:
        """
        恢复技能到指定版本
        
        Args:
            skill_name: 技能名称
            version: 版本号
            
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        try:
            history = self.get_skill_history(skill_name)
            
            target_version = None
            for v in history:
                if v.version == version:
                    target_version = v
                    break
            
            if not target_version:
                return False, f"版本不存在：{version}"
            
            # 创建当前版本的备份
            self._create_backup(skill_name)
            
            # 恢复到指定版本
            success = self._save_skill_updates(skill_name, target_version.skill_data)
            
            if success:
                # 记录恢复操作
                restore_change = SkillChange(
                    timestamp=datetime.now().isoformat(),
                    change_type='restore',
                    field='all',
                    old_value='current',
                    new_value=version,
                    reason=f'恢复到版本 {version}'
                )
                self._record_changes(skill_name, [restore_change])
            
            return success, None if success else "恢复失败"
            
        except Exception as e:
            return False, f"恢复失败：{str(e)}"
    
    def compare_skill_versions(self, skill_name: str, version1: str, version2: str) -> Dict[str, Any]:
        """
        比较两个版本的差异
        
        Args:
            skill_name: 技能名称
            version1: 版本1
            version2: 版本2
            
        Returns:
            Dict[str, Any]: 比较结果
        """
        history = self.get_skill_history(skill_name)
        
        v1_data = None
        v2_data = None
        
        for v in history:
            if v.version == version1:
                v1_data = v.skill_data
            elif v.version == version2:
                v2_data = v.skill_data
        
        if not v1_data or not v2_data:
            return {'error': '版本不存在'}
        
        differences = self._compare_skill_data(v1_data, v2_data)
        
        return {
            'version1': version1,
            'version2': version2,
            'differences': differences,
            'summary': f"发现 {len(differences)} 处差异"
        }
    
    # 私有辅助方法
    def _get_skill_info(self, skill_dir: Path) -> Optional[Dict[str, Any]]:
        """获取技能基本信息"""
        try:
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                return None
            
            # 解析基本信息
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取 name 和 description
            name = skill_dir.name
            description = ""
            
            # 简单解析 frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('description:'):
                            description = line.replace('description:', '').strip().strip('|')
                            break
            
            # 获取文件信息
            stat = skill_file.stat()
            
            return {
                'name': name,
                'description': description[:100] + '...' if len(description) > 100 else description,
                'path': str(skill_dir),
                'last_modified': stat.st_mtime,
                'size': stat.st_size
            }
            
        except Exception:
            return None
    
    def _parse_skill_file(self, skill_file: Path) -> Dict[str, Any]:
        """解析 SKILL.md 文件"""
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        skill_data = {}
        
        # 解析 frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]
                
                for line in frontmatter.split('\n'):
                    line = line.strip()
                    if line.startswith('name:'):
                        skill_data['name'] = line.replace('name:', '').strip()
                    elif line.startswith('description:'):
                        skill_data['description'] = line.replace('description:', '').strip().strip('|')
                    elif line.startswith('dependencies:'):
                        deps = line.replace('dependencies:', '').strip('[]')
                        skill_data['dependencies'] = [d.strip() for d in deps.split(',') if d.strip()]
                
                # 解析正文
                skill_data.update(self._parse_skill_body(body))
        
        return skill_data
    
    def _parse_skill_body(self, body: str) -> Dict[str, Any]:
        """解析 SKILL.md 正文"""
        data = {}
        
        lines = body.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('# ') and not current_section:
                # 技能名称后的第一段通常是简介
                continue
            elif line.startswith('## ') and not current_section:
                current_section = line.replace('## ', '').strip()
                section_content = []
            elif line.startswith('## ') and current_section:
                # 保存上一个section
                data[current_section] = '\n'.join(section_content).strip()
                current_section = line.replace('## ', '').strip()
                section_content = []
            elif current_section:
                if line.startswith('1. ') or line.startswith('- '):
                    section_content.append(line)
                elif line and not line.startswith('#'):
                    section_content.append(line)
        
        # 保存最后一个section
        if current_section and section_content:
            data[current_section] = '\n'.join(section_content).strip()
        
        # 提取特定字段
        if '执行步骤' in data:
            steps = []
            for line in data['执行步骤'].split('\n'):
                if line.strip().startswith(('. ', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                    step = line.strip()[2:].strip()
                    if step:
                        steps.append(step)
            data['steps'] = steps
        
        if '注意事项' in data:
            notes = []
            for line in data['注意事项'].split('\n'):
                if line.strip().startswith('- '):
                    note = line.strip()[2:].strip()
                    if note:
                        notes.append(note)
            data['notes'] = notes
        
        if '输入' in data:
            data['input_desc'] = data['输入']
        
        if '输出' in data:
            data['output_desc'] = data['输出']
        
        # 提取第一段作为简介
        all_lines = [line.strip() for line in body.split('\n') if line.strip() and not line.startswith('#')]
        if all_lines:
            data['summary'] = all_lines[0]
        
        return data
    
    def _read_additional_files(self, skill_dir: Path) -> Dict[str, Any]:
        """读取附加文件信息"""
        data = {}
        
        # 检查各种目录
        data['has_scripts'] = (skill_dir / 'scripts').exists()
        data['has_refs'] = (skill_dir / 'references').exists()
        data['has_assets'] = (skill_dir / 'assets').exists()
        data['has_evals'] = (skill_dir / 'evals').exists()
        
        return data
    
    def _detect_changes(self, current: Dict[str, Any], updates: Dict[str, Any], reason: str) -> List[SkillChange]:
        """检测变更"""
        changes = []
        timestamp = datetime.now().isoformat()
        
        for field, new_value in updates.items():
            old_value = current.get(field)
            
            if old_value != new_value:
                change = SkillChange(
                    timestamp=timestamp,
                    change_type='update',
                    field=field,
                    old_value=old_value,
                    new_value=new_value,
                    reason=reason
                )
                changes.append(change)
        
        return changes
    
    def _validate_skill_data(self, skill_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证技能数据"""
        errors = []
        
        # 必填字段
        if not skill_data.get('name'):
            errors.append("技能名称不能为空")
        
        if not skill_data.get('description'):
            errors.append("触发描述不能为空")
        
        # 名称格式
        name = skill_data.get('name', '')
        if not self._validate_skill_name(name):
            errors.append("技能名称格式不正确")
        
        return len(errors) == 0, errors
    
    def _validate_skill_name(self, name: str) -> bool:
        """验证技能名称格式"""
        import re
        return bool(re.match(r'^[a-z0-9-]+$', name))
    
    def _save_skill_updates(self, skill_name: str, skill_data: Dict[str, Any]) -> bool:
        """保存技能更新"""
        try:
            from scripts.create_skill import create_skill_structure
            
            # 使用现有的创建脚本重新生成文件
            result = create_skill_structure(skill_data, str(self.skills_dir))
            
            return result.get('success', False)
            
        except Exception as e:
            print(f"保存失败：{e}")
            return False
    
    def _create_backup(self, skill_name: str) -> bool:
        """创建备份"""
        try:
            skill_dir = self.skills_dir / skill_name
            if not skill_dir.exists():
                return True
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_dir / f"{skill_name}_{timestamp}"
            
            shutil.copytree(skill_dir, backup_dir)
            return True
            
        except Exception as e:
            print(f"创建备份失败：{e}")
            return False
    
    def _record_changes(self, skill_name: str, changes: List[SkillChange]) -> None:
        """记录变更历史"""
        history_file = self.backup_dir / f"{skill_name}_history.json"
        
        try:
            # 读取现有历史
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            else:
                history_data = {'versions': []}
            
            # 添加新版本
            version = f"v{len(history_data['versions']) + 1}"
            new_version = SkillVersion(
                version=version,
                timestamp=datetime.now().isoformat(),
                changes=changes,
                description=changes[0].reason if changes else "更新",
                skill_data={}  # 这里应该包含完整的技能数据
            )
            
            history_data['versions'].append(asdict(new_version))
            
            # 保存历史
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"记录变更失败：{e}")
    
    def _update_skill_name_in_files(self, skill_dir: Path, new_name: str) -> None:
        """更新文件中的技能名称"""
        try:
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                with open(skill_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 更新 frontmatter 中的 name
                content = content.replace(f"name: {skill_dir.name}", f"name: {new_name}")
                
                with open(skill_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except Exception as e:
            print(f"更新文件内容失败：{e}")
    
    def _compare_skill_data(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """比较两个技能数据"""
        differences = []
        
        all_keys = set(data1.keys()) | set(data2.keys())
        
        for key in all_keys:
            val1 = data1.get(key)
            val2 = data2.get(key)
            
            if val1 != val2:
                differences.append({
                    'field': key,
                    'old': val1,
                    'new': val2,
                    'type': 'changed' if val1 is not None and val2 is not None else 'added' if val2 is not None else 'removed'
                })
        
        return differences


# 全局更新器实例
skill_updater = SkillUpdater()
