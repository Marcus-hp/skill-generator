#!/usr/bin/env python3
"""
intelligent_recommender.py

智能化模板和关键词推荐系统。
基于技能类型和用户描述，智能推荐合适的模板、名称和关键词。
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class SkillTemplate:
    """技能模板"""
    name: str
    category: str
    description_template: str
    name_suggestions: List[str]
    keywords: Dict[str, List[str]]  # 中文和英文关键词
    dependencies: List[str]
    steps_template: List[str]
    notes_template: List[str]
    input_output: Dict[str, str]


@dataclass
class NameSuggestion:
    """名称建议"""
    name: str
    reason: str
    confidence: float


class IntelligentRecommender:
    """智能推荐器"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.keyword_mappings = self._load_keyword_mappings()
        self.name_patterns = self._load_name_patterns()
    
    def _load_templates(self) -> Dict[str, SkillTemplate]:
        """加载技能模板"""
        templates = {
            'file_processing': SkillTemplate(
                name='文件处理',
                category='file',
                description_template="""当用户想要创建或处理{file_type}文件时使用此技能。
触发场景包括：{scenarios}。
触发关键词：{chinese_keywords}，{english_keywords}。
即使用户没有明确说"生成文件"，只要需要输出{file_type}格式的内容，都应使用此技能。""",
                name_suggestions=['{type}-creator', '{type}-generator', '{type}-processor'],
                keywords={
                    'chinese': ['生成文件', '创建文档', '制作{type}', '{type}文档', '文档处理'],
                    'english': ['create {type}', 'generate {type}', '{type} creator', 'document']
                },
                dependencies=['python-docx', 'reportlab', 'openpyxl'],
                steps_template=[
                    "读取用户需求，确认{file_type}类型和内容结构",
                    "加载对应的模板文件（如有）",
                    "使用脚本生成{file_type}内容",
                    "校验文件格式是否正确",
                    "保存到输出目录并提供下载链接"
                ],
                notes_template=[
                    "文件大小建议不超过 50MB",
                    "不支持加密或受保护的文件",
                    "图片嵌入需确保格式为 PNG 或 JPG"
                ],
                input_output={
                    'input': '用户提供的文字描述或模板文件',
                    'output': '生成的{file_type}格式文件'
                }
            ),
            
            'data_analysis': SkillTemplate(
                name='数据分析',
                category='data',
                description_template="""当用户需要分析数据、生成图表、处理{data_format}文件时使用此技能。
触发场景：{scenarios}。
触发关键词：{chinese_keywords}，{english_keywords}。
支持从数据探索到完整报告生成的全流程分析。""",
                name_suggestions=['data-analyst', '{type}-analyzer', 'insight-generator'],
                keywords={
                    'chinese': ['数据分析', '统计', '图表', '可视化', '数据清洗', '趋势分析'],
                    'english': ['data analysis', 'statistics', 'visualization', 'chart', 'analytics']
                },
                dependencies=['pandas', 'matplotlib', 'seaborn', 'openpyxl'],
                steps_template=[
                    "加载数据文件，检查数据结构和质量",
                    "清洗数据（处理缺失值、异常值）",
                    "执行描述性统计分析",
                    "生成可视化图表",
                    "撰写分析摘要，输出报告"
                ],
                notes_template=[
                    "数据行数超过 10 万行时提示用户可能需要较长时间",
                    "不支持实时数据流，仅支持静态文件",
                    "图表中文字需确保字体支持中文显示"
                ],
                input_output={
                    'input': 'CSV、Excel 或其他格式的数据文件',
                    'output': '分析报告和可视化图表'
                }
            ),
            
            'code_assistant': SkillTemplate(
                name='代码辅助',
                category='code',
                description_template="""当用户需要代码审查、调试、重构或生成{language}代码时使用此技能。
触发场景：{scenarios}。
触发关键词：{chinese_keywords}，{english_keywords}。
专注于代码质量提升和问题解决。""",
                name_suggestions=['{lang}-assistant', 'code-reviewer', '{lang}-optimizer'],
                keywords={
                    'chinese': ['代码审查', '调试', '重构', '帮我写代码', '代码优化', 'bug修复'],
                    'english': ['code review', 'debug', 'refactor', 'code generation', 'optimize']
                },
                dependencies=[],
                steps_template=[
                    "阅读并理解代码逻辑和用户目标",
                    "识别问题或改进点（性能、可读性、安全性）",
                    "起草修改方案",
                    "生成改进后的代码",
                    "解释变更原因，列出改动清单"
                ],
                notes_template=[
                    "代码超过 500 行时建议分模块处理",
                    "不执行用户的代码，只分析和生成",
                    "保持原有代码风格和约定"
                ],
                input_output={
                    'input': '代码文件或代码片段',
                    'output': '改进后的代码和修改说明'
                }
            ),
            
            'research': SkillTemplate(
                name='搜索研究',
                category='research',
                description_template="""当用户需要深度研究{topic}、对比信息或生成调研报告时使用此技能。
触发场景：{scenarios}。
触发关键词：{chinese_keywords}，{english_keywords}。
提供全面、准确的研究结果。""",
                name_suggestions=['deep-researcher', '{topic}-analyst', 'intelligence-collector'],
                keywords={
                    'chinese': ['研究', '调研', '搜索', '报告', '对比', '最新', '了解一下'],
                    'english': ['research', 'investigate', 'analysis', 'report', 'comparison']
                },
                dependencies=[],
                steps_template=[
                    "分解研究问题，确定搜索维度",
                    "执行多角度网络搜索",
                    "筛选高质量信息源，过滤低质内容",
                    "综合分析，识别共识与分歧",
                    "撰写结构化报告，附来源列表"
                ],
                notes_template=[
                    "时效性强的信息以最近 6 个月内的来源为准",
                    "涉及医疗/法律建议需加免责声明",
                    "优先选择权威来源和学术资料"
                ],
                input_output={
                    'input': '研究主题或问题描述',
                    'output': '结构化调研报告'
                }
            ),
            
            'automation': SkillTemplate(
                name='流程自动化',
                category='automation',
                description_template="""当用户需要自动执行{task_type}、批量处理或自动化工作流时使用此技能。
触发场景：{scenarios}。
触发关键词：{chinese_keywords}，{english_keywords}。
提高工作效率，减少重复操作。""",
                name_suggestions=['workflow-automator', '{task}-processor', 'batch-executor'],
                keywords={
                    'chinese': ['自动化', '批量', '工作流', '自动执行', '流程', 'pipeline'],
                    'english': ['automation', 'batch', 'workflow', 'pipeline', 'process']
                },
                dependencies=['bash'],
                steps_template=[
                    "理解工作流程的输入、步骤和预期输出",
                    "拆分任务为可执行的子步骤",
                    "逐步执行，每步确认结果",
                    "处理异常情况，提供失败回滚方案",
                    "汇总执行结果，输出操作日志"
                ],
                notes_template=[
                    "每步执行前确认，避免不可逆操作",
                    "批量任务超过 50 个时建议先用小样本测试",
                    "提供详细的执行日志和错误信息"
                ],
                input_output={
                    'input': '任务描述和相关文件',
                    'output': '执行结果和操作日志'
                }
            )
        }
        
        return templates
    
    def _load_keyword_mappings(self) -> Dict[str, List[str]]:
        """加载关键词映射"""
        return {
            'file': ['文档', '文件', 'word', 'pdf', 'excel', 'ppt', '报告', '表格', '演示文稿'],
            'data': ['数据', '分析', '统计', '图表', '可视化', 'csv', 'excel', '数据集'],
            'code': ['代码', '编程', '开发', 'bug', '调试', '优化', '重构', '审查'],
            'research': ['研究', '调研', '搜索', '了解', '分析', '报告', '对比'],
            'automation': ['自动化', '批量', '流程', '工作流', '重复', '执行']
        }
    
    def _load_name_patterns(self) -> Dict[str, List[str]]:
        """加载命名模式"""
        return {
            'file': ['{type}-creator', '{type}-generator', 'doc-{type}', '{type}-maker'],
            'data': ['data-{type}', '{type}-analyzer', 'insight-{type}', '{type}-viz'],
            'code': ['{lang}-helper', 'code-{type}', '{lang}-fixer', '{lang}-writer'],
            'research': ['{topic}-research', 'deep-{topic}', '{topic}-analysis', 'smart-{topic}'],
            'automation': ['auto-{task}', '{task}-flow', 'batch-{task}', '{task}-bot']
        }
    
    def recommend_category(self, user_description: str) -> Tuple[str, float]:
        """
        推荐技能类别
        
        Args:
            user_description: 用户描述
            
        Returns:
            Tuple[str, float]: (推荐类别, 置信度)
        """
        description_lower = user_description.lower()
        scores = {}
        
        for category, keywords in self.keyword_mappings.items():
            score = 0
            for keyword in keywords:
                if keyword in description_lower:
                    score += 1
            scores[category] = score
        
        if not scores or max(scores.values()) == 0:
            return 'other', 0.0
        
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category] / len(self.keyword_mappings[best_category])
        
        return best_category, confidence
    
    def recommend_names(self, category: str, user_description: str, 
                       count: int = 3) -> List[NameSuggestion]:
        """
        推荐技能名称
        
        Args:
            category: 技能类别
            user_description: 用户描述
            count: 推荐数量
            
        Returns:
            List[NameSuggestion]: 名称建议列表
        """
        if category not in self.templates:
            # 尝试映射类别名称
            category_mapping = {
                'file': 'file_processing',
                'data': 'data_analysis', 
                'code': 'code_assistant',
                'research': 'research',
                'automation': 'automation'
            }
            category = category_mapping.get(category, 'file_processing')  # 默认类别
        
        template = self.templates[category]
        suggestions = []
        
        # 提取关键信息
        file_types = self._extract_file_types(user_description)
        languages = self._extract_languages(user_description)
        topics = self._extract_topics(user_description)
        tasks = self._extract_tasks(user_description)
        
        # 生成名称建议
        base_patterns = self.name_patterns.get(category, ['skill-{type}'])
        
        for i, pattern in enumerate(base_patterns[:count]):
            name = self._generate_name_from_pattern(pattern, file_types, languages, topics, tasks)
            reason = self._generate_name_reason(name, category, file_types, languages, topics)
            confidence = self._calculate_name_confidence(name, user_description)
            
            suggestions.append(NameSuggestion(name=name, reason=reason, confidence=confidence))
        
        # 按置信度排序
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:count]
    
    def recommend_keywords(self, category: str, user_description: str) -> Dict[str, List[str]]:
        """
        推荐关键词
        
        Args:
            category: 技能类别
            user_description: 用户描述
            
        Returns:
            Dict[str, List[str]]: 中英文关键词
        """
        if category not in self.templates:
            # 尝试映射类别名称
            category_mapping = {
                'file': 'file_processing',
                'data': 'data_analysis', 
                'code': 'code_assistant',
                'research': 'research',
                'automation': 'automation'
            }
            category = category_mapping.get(category, 'file_processing')
        
        template = self.templates[category]
        base_keywords = template.keywords.copy()
        
        # 从用户描述中提取额外关键词
        extracted_keywords = self._extract_keywords_from_description(user_description)
        
        # 合并并去重
        final_keywords = {
            'chinese': list(set(base_keywords['chinese'] + extracted_keywords['chinese'])),
            'english': list(set(base_keywords['english'] + extracted_keywords['english']))
        }
        
        return final_keywords
    
    def generate_description(self, category: str, user_description: str, 
                          skill_name: str) -> str:
        """
        生成触发描述
        
        Args:
            category: 技能类别
            user_description: 用户描述
            skill_name: 技能名称
            
        Returns:
            str: 生成的描述
        """
        if category not in self.templates:
            category = 'file'
        
        template = self.templates[category]
        keywords = self.recommend_keywords(category, user_description)
        
        # 提取场景信息
        scenarios = self._extract_scenarios(user_description, category)
        file_types = self._extract_file_types(user_description)
        
        # 填充模板
        description = template.description_template.format(
            file_type=file_types[0] if file_types else '文档',
            scenarios='、'.join(scenarios),
            chinese_keywords='、'.join(keywords['chinese'][:5]),
            english_keywords='、'.join(keywords['english'][:5])
        )
        
        return description
    
    def recommend_dependencies(self, category: str, user_description: str) -> List[str]:
        """
        推荐依赖库
        
        Args:
            category: 技能类别
            user_description: 用户描述
            
        Returns:
            List[str]: 推荐的依赖库
        """
        if category not in self.templates:
            return []
        
        base_deps = self.templates[category].dependencies
        
        # 根据用户描述添加特定依赖
        additional_deps = []
        
        if 'pdf' in user_description.lower():
            additional_deps.extend(['pdfplumber', 'PyPDF2'])
        elif 'image' in user_description.lower() or '图片' in user_description:
            additional_deps.extend(['Pillow', 'opencv-python'])
        elif 'web' in user_description.lower() or '网页' in user_description:
            additional_deps.extend(['requests', 'beautifulsoup4'])
        elif 'email' in user_description.lower() or '邮件' in user_description:
            additional_deps.extend(['smtplib', 'email'])
        
        return list(set(base_deps + additional_deps))
    
    # 私有辅助方法
    def _extract_file_types(self, description: str) -> List[str]:
        """提取文件类型"""
        file_types = []
        patterns = {
            'word': r'\b(word|docx?|\.doc)\b',
            'pdf': r'\b(pdf|\.pdf)\b',
            'excel': r'\b(excel|xlsx?|\.xls)\b',
            'ppt': r'\b(ppt|pptx?|\.ppt)\b',
            'csv': r'\b(csv|\.csv)\b'
        }
        
        for file_type, pattern in patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                file_types.append(file_type)
        
        return file_types or ['文档']
    
    def _extract_languages(self, description: str) -> List[str]:
        """提取编程语言"""
        languages = []
        lang_patterns = {
            'python': r'\bpython\b',
            'javascript': r'\b(javascript|js|node)\b',
            'java': r'\bjava\b',
            'cpp': r'\b(c\+\+|cpp)\b',
            'html': r'\bhtml\b',
            'css': r'\bcss\b'
        }
        
        for lang, pattern in lang_patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                languages.append(lang)
        
        return languages
    
    def _extract_topics(self, description: str) -> List[str]:
        """提取主题"""
        # 简单的主题提取，实际应用中可以使用更复杂的NLP
        topics = []
        topic_keywords = ['市场', '技术', '产品', '用户', '竞品', '行业', '趋势']
        
        for keyword in topic_keywords:
            if keyword in description:
                topics.append(keyword)
        
        return topics
    
    def _extract_tasks(self, description: str) -> List[str]:
        """提取任务类型"""
        tasks = []
        task_keywords = ['发送', '处理', '生成', '分析', '转换', '整理', '备份']
        
        for keyword in task_keywords:
            if keyword in description:
                tasks.append(keyword)
        
        return tasks
    
    def _generate_name_from_pattern(self, pattern: str, file_types: List[str],
                                 languages: List[str], topics: List[str],
                                 tasks: List[str]) -> str:
        """根据模式生成名称"""
        replacements = {}
        
        if file_types and len(file_types) > 0:
            replacements['{type}'] = file_types[0]
        elif languages and len(languages) > 0:
            replacements['{lang}'] = languages[0]
        elif topics and len(topics) > 0:
            replacements['{topic}'] = topics[0]
        elif tasks and len(tasks) > 0:
            replacements['{task}'] = tasks[0]
        else:
            replacements['{type}'] = 'document'
        
        name = pattern
        for placeholder, value in replacements.items():
            name = name.replace(placeholder, value)
        
        return name
    
    def _generate_name_reason(self, name: str, category: str,
                            file_types: List[str], languages: List[str],
                            topics: List[str]) -> str:
        """生成名称推荐理由"""
        reasons = []
        
        if file_types:
            reasons.append(f"针对{file_types[0]}文件类型")
        if languages:
            reasons.append(f"支持{languages[0]}语言")
        if topics:
            reasons.append(f"专注{topics[0]}领域")
        
        if not reasons:
            reasons.append("简洁易记的命名")
        
        return "，".join(reasons)
    
    def _calculate_name_confidence(self, name: str, description: str) -> float:
        """计算名称推荐置信度"""
        confidence = 0.5  # 基础置信度
        
        # 如果名称中包含描述中的关键词，提高置信度
        name_lower = name.lower()
        desc_lower = description.lower()
        
        for word in name_lower.split('-'):
            if word in desc_lower:
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _extract_keywords_from_description(self, description: str) -> Dict[str, List[str]]:
        """从描述中提取关键词"""
        chinese_keywords = []
        english_keywords = []
        
        # 简单的关键词提取
        chinese_words = re.findall(r'[\u4e00-\u9fff]+', description)
        english_words = re.findall(r'\b[a-zA-Z]+\b', description)
        
        # 过滤掉太短的词
        chinese_keywords = [word for word in chinese_words if len(word) >= 2]
        english_keywords = [word for word in english_words if len(word) >= 3]
        
        return {'chinese': chinese_keywords, 'english': english_keywords}
    
    def _extract_scenarios(self, description: str, category: str) -> List[str]:
        """提取使用场景"""
        base_scenarios = {
            'file': ['生成文档', '格式转换', '批量处理'],
            'data': ['数据清洗', '统计分析', '可视化展示'],
            'code': ['代码审查', '性能优化', 'bug修复'],
            'research': ['信息收集', '对比分析', '报告撰写'],
            'automation': ['批量执行', '流程优化', '任务自动化']
        }
        
        return base_scenarios.get(category, ['通用处理'])


# 全局推荐器实例
intelligent_recommender = IntelligentRecommender()
