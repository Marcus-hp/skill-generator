#!/usr/bin/env python3
"""
session_manager.py

会话进度管理模块，支持技能创建过程的保存和恢复。
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SkillCreationSession:
    """技能创建会话数据结构"""
    session_id: str
    start_time: float
    current_step: int
    total_steps: int
    skill_data: Dict[str, Any]
    is_completed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillCreationSession':
        """从字典创建实例"""
        return cls(**data)


class SessionManager:
    """会话管理器"""
    
    def __init__(self, session_dir: str = ".claude/skills/sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[SkillCreationSession] = None
    
    def create_session(self, skill_data: Dict[str, Any]) -> str:
        """
        创建新的技能创建会话
        
        Args:
            skill_data: 初始技能数据
            
        Returns:
            str: 会话ID
        """
        session_id = f"skill_{int(time.time())}"
        session = SkillCreationSession(
            session_id=session_id,
            start_time=time.time(),
            current_step=0,
            total_steps=8,
            skill_data=skill_data
        )
        
        self.current_session = session
        self._save_session(session)
        return session_id
    
    def update_session(self, step: int, skill_data: Dict[str, Any]) -> bool:
        """
        更新会话进度
        
        Args:
            step: 当前步骤
            skill_data: 更新后的技能数据
            
        Returns:
            bool: 更新是否成功
        """
        if not self.current_session:
            return False
        
        self.current_session.current_step = step
        self.current_session.skill_data = skill_data
        self.current_session.is_completed = (step >= self.current_session.total_steps)
        
        return self._save_session(self.current_session)
    
    def load_session(self, session_id: str) -> Optional[SkillCreationSession]:
        """
        加载指定会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[SkillCreationSession]: 会话数据，如果不存在返回None
        """
        session_file = self.session_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = SkillCreationSession.from_dict(data)
            self.current_session = session
            return session
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"加载会话失败: {e}")
            return None
    
    def list_sessions(self) -> list[Dict[str, Any]]:
        """
        列出所有会话
        
        Returns:
            list: 会话信息列表
        """
        sessions = []
        
        for session_file in self.session_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 简化信息用于列表显示
                sessions.append({
                    'session_id': data['session_id'],
                    'start_time': data['start_time'],
                    'current_step': data['current_step'],
                    'total_steps': data['total_steps'],
                    'is_completed': data['is_completed'],
                    'skill_name': data['skill_data'].get('name', '未命名'),
                    'last_modified': session_file.stat().st_mtime
                })
                
            except (json.JSONDecodeError, KeyError):
                continue
        
        # 按最后修改时间排序
        sessions.sort(key=lambda x: x['last_modified'], reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除指定会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 删除是否成功
        """
        session_file = self.session_dir / f"{session_id}.json"
        
        if session_file.exists():
            session_file.unlink()
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
            return True
        
        return False
    
    def cleanup_old_sessions(self, days: int = 7) -> int:
        """
        清理过期会话
        
        Args:
            days: 保留天数
            
        Returns:
            int: 清理的会话数量
        """
        cutoff_time = time.time() - (days * 24 * 3600)
        cleaned = 0
        
        for session_file in self.session_dir.glob("*.json"):
            if session_file.stat().st_mtime < cutoff_time:
                session_file.unlink()
                cleaned += 1
        
        return cleaned
    
    def _save_session(self, session: SkillCreationSession) -> bool:
        """
        保存会话到文件
        
        Args:
            session: 会话数据
            
        Returns:
            bool: 保存是否成功
        """
        session_file = self.session_dir / f"{session.session_id}.json"
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
            return True
            
        except (OSError, TypeError) as e:
            print(f"保存会话失败: {e}")
            return False
    
    def get_progress_summary(self) -> Optional[Dict[str, Any]]:
        """
        获取当前会话的进度摘要
        
        Returns:
            Optional[Dict]: 进度信息，如果没有当前会话返回None
        """
        if not self.current_session:
            return None
        
        return {
            'session_id': self.current_session.session_id,
            'current_step': self.current_session.current_step,
            'total_steps': self.current_session.total_steps,
            'progress_percent': (self.current_session.current_step / self.current_session.total_steps) * 100,
            'is_completed': self.current_session.is_completed,
            'skill_name': self.current_session.skill_data.get('name', '未命名')
        }


# 全局会话管理器实例
session_manager = SessionManager()
