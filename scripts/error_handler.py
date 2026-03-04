#!/usr/bin/env python3
"""
error_handler.py

增强的错误处理和用户提示模块。
提供友好的错误信息、输入验证和恢复建议。
"""

import re
import sys
import os
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime


class UserInputError(Exception):
    """用户输入错误"""
    def __init__(self, message: str, suggestions: List[str] = None):
        super().__init__(message)
        self.suggestions = suggestions or []


class SkillValidationError(Exception):
    """技能验证错误"""
    def __init__(self, message: str, field: str = None, fix_suggestion: str = None):
        super().__init__(message)
        self.field = field
        self.fix_suggestion = fix_suggestion


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_patterns = {
            'invalid_choice': r'^(?:无效|错误|不对|不正确)',
            'go_back': r'^(?:返回|回去|上一步|回到上一步|back|go back)',
            'restart': r'^(?:重来|重新开始|restart|重新来)',
            'save': r'^(?:保存|save|保存进度)',
            'help': r'^(?:帮助|help|怎么用|怎么办)',
            'quit': r'^(?:退出|quit|结束|停止)',
            'skip': r'^(?:跳过|skip|略过)',
            'modify': r'^(?:修改|modify|改|更改)',
            'preview': r'^(?:预览|preview|看看|显示)',
        }
        
        self.friendly_messages = {
            'invalid_choice': "🤔 这个选项不太对，请从下面的数字中选择：",
            'invalid_input': "📝 我没太理解，能换个说法吗？",
            'file_error': "📁 文件操作出了点问题：",
            'network_error': "🌐 网络连接似乎有问题：",
            'validation_error': "⚠️ 信息检查发现一些问题：",
            'system_error': "🔧 系统遇到了意外情况：",
        }
    
    def parse_user_intent(self, user_input: str) -> Tuple[str, Optional[str]]:
        """
        解析用户意图
        
        Args:
            user_input: 用户输入
            
        Returns:
            Tuple[str, Optional[str]]: (意图类型, 提取的参数)
        """
        user_input = user_input.strip().lower()
        
        for intent, pattern in self.error_patterns.items():
            match = re.match(pattern, user_input, re.IGNORECASE)
            if match:
                # 尝试提取参数
                remaining = user_input[len(match.group(0)):].strip()
                return intent, remaining if remaining else None
        
        return 'normal_input', user_input
    
    def validate_skill_name(self, name: str) -> Tuple[bool, Optional[str]]:
        """
        验证技能名称
        
        Args:
            name: 技能名称
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not name:
            return False, "技能名称不能为空"
        
        if len(name) < 3:
            return False, "技能名称至少需要3个字符"
        
        if len(name) > 50:
            return False, "技能名称不能超过50个字符"
        
        # 检查命名规范（小写字母、数字、连字符）
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, "技能名称只能包含小写字母、数字和连字符"
        
        # 检查是否以连字符开头或结尾
        if name.startswith('-') or name.endswith('-'):
            return False, "技能名称不能以连字符开头或结尾"
        
        # 检查连续连字符
        if '--' in name:
            return False, "技能名称不能包含连续的连字符"
        
        return True, None
    
    def validate_description(self, description: str) -> Tuple[bool, Optional[str]]:
        """
        验证触发描述
        
        Args:
            description: 触发描述
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not description:
            return False, "触发描述不能为空"
        
        if len(description) < 50:
            return False, "触发描述太短，建议至少50个字符，包含更多场景和关键词"
        
        if len(description) > 300:
            return False, "触发描述太长，建议控制在300字符以内"
        
        # 检查是否包含关键词
        keywords = ['触发', '关键词', '场景', '使用']
        has_keyword = any(keyword in description for keyword in keywords)
        
        if not has_keyword:
            return False, "建议在描述中明确说明触发场景和关键词"
        
        return True, None
    
    def validate_file_path(self, path: str) -> Tuple[bool, Optional[str]]:
        """
        验证文件路径
        
        Args:
            path: 文件路径
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        try:
            path_obj = Path(path)
            
            # 检查路径格式
            if not path_obj.is_absolute():
                return False, "请提供绝对路径"
            
            # 检查父目录是否存在
            parent_dir = path_obj.parent
            if not parent_dir.exists():
                return False, f"父目录不存在：{parent_dir}"
            
            # 检查是否有写入权限
            if not os.access(parent_dir, os.W_OK):
                return False, f"没有写入权限：{parent_dir}"
            
            return True, None
            
        except Exception as e:
            return False, f"路径格式错误：{str(e)}"
    
    def format_error_message(self, error_type: str, details: str, 
                           suggestions: List[str] = None) -> str:
        """
        格式化错误消息
        
        Args:
            error_type: 错误类型
            details: 错误详情
            suggestions: 建议列表
            
        Returns:
            str: 格式化的错误消息
        """
        base_msg = self.friendly_messages.get(error_type, "❌ 出现了问题：")
        
        message = f"{base_msg}\n\n{details}"
        
        if suggestions:
            message += "\n\n💡 建议："
            for i, suggestion in enumerate(suggestions, 1):
                message += f"\n{i}. {suggestion}"
        
        return message
    
    def get_recovery_options(self, error_type: str) -> List[str]:
        """
        获取错误恢复选项
        
        Args:
            error_type: 错误类型
            
        Returns:
            List[str]: 恢复选项列表
        """
        common_options = [
            "重新输入",
            "回到上一步",
            "查看帮助"
        ]
        
        specific_options = {
            'invalid_choice': ["查看所有选项", "输入具体描述"],
            'file_error': ["检查路径是否正确", "选择其他路径", "创建到默认路径"],
            'validation_error': ["修改错误字段", "使用默认值", "跳过此步骤"],
            'network_error': ["稍后重试", "使用离线模式", "检查网络连接"],
            'system_error': ["重启程序", "清除缓存", "联系技术支持"]
        }
        
        return common_options + specific_options.get(error_type, [])
    
    def create_error_report(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建错误报告
        
        Args:
            error: 异常对象
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 错误报告
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'traceback': sys.exc_info()[2] if sys.exc_info()[2] else None,
            'suggestions': self.get_recovery_options(type(error).__name__.lower())
        }
    
    def handle_user_input_error(self, user_input: str, valid_options: List[str] = None) -> str:
        """
        处理用户输入错误
        
        Args:
            user_input: 用户输入
            valid_options: 有效选项列表
            
        Returns:
            str: 友好的错误提示
        """
        intent, param = self.parse_user_intent(user_input)
        
        if intent == 'help':
            return self._generate_help_message(valid_options)
        elif intent == 'invalid_choice' and valid_options:
            return self.format_error_message(
                'invalid_choice',
                f"有效选项是：{', '.join(valid_options)}",
                ["直接回复数字", "描述你想要的功能"]
            )
        else:
            return self.format_error_message(
                'invalid_input',
                f"我理解你说的是：'{user_input}'",
                ["尝试用更简单的表达", "查看可用选项", "说'帮助'获取指导"]
            )
    
    def _generate_help_message(self, valid_options: List[str] = None) -> str:
        """
        生成帮助消息
        
        Args:
            valid_options: 有效选项列表
            
        Returns:
            str: 帮助消息
        """
        help_msg = """📖 **使用帮助**

**基本操作：**
- 回复数字选择选项
- 说"修改"调整刚才的内容  
- 说"回到上一步"返回上一题
- 说"重来"重新开始
- 说"保存进度"保存当前会话
- 说"预览"查看当前技能信息

**输入技巧：**
- 尽量用简洁的语言描述
- 可以同时使用中英文
- 不确定时可以说"帮我推荐"

"""
        
        if valid_options:
            help_msg += f"**当前可用选项：**\n"
            for i, option in enumerate(valid_options, 1):
                help_msg += f"{i}. {option}\n"
        
        return help_msg


# 全局错误处理器实例
error_handler = ErrorHandler()
