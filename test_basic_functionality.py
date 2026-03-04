#!/usr/bin/env python3
"""
test_basic_functionality.py

测试基础功能的脚本
"""

import json
import sys
import os
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def test_basic_skill_creation():
    """测试基础技能创建功能"""
    print("🧪 开始测试基础技能创建功能...")
    
    # 测试配置
    test_config = {
        "name": "test-skill",
        "description": "Test skill for validation. This is a test description that meets the minimum length requirement and includes keywords like trigger and scenarios.",
        "summary": "A test skill for validation",
        "steps": [
            "Read user input and validate format",
            "Process the data according to requirements", 
            "Generate output and save results"
        ],
        "input_desc": "User provides text input for processing",
        "output_desc": "Processed results and summary report"
    }
    
    try:
        # 导入创建脚本
        from create_skill import create_skill_structure
        
        print("✅ 成功导入 create_skill 模块")
        
        # 测试创建技能结构
        result = create_skill_structure(test_config, "./test_output")
        
        if result.get('success'):
            print("✅ 技能创建成功!")
            print(f"   路径: {result['path']}")
            print(f"   文件: {result['files_created']}")
            
            # 验证文件是否真的创建了
            skill_path = Path(result['path'])
            if skill_path.exists():
                print("✅ 技能目录创建成功")
                
                # 检查必需文件
                required_files = ['SKILL.md', 'README.md']
                for file_name in required_files:
                    file_path = skill_path / file_name
                    if file_path.exists():
                        print(f"✅ {file_name} 创建成功")
                    else:
                        print(f"❌ {file_name} 创建失败")
                
                # 读取并显示SKILL.md内容预览
                skill_md = skill_path / 'SKILL.md'
                if skill_md.exists():
                    content = skill_md.read_text(encoding='utf-8')
                    print("\n📄 SKILL.md 预览 (前200字符):")
                    print(content[:200] + "..." if len(content) > 200 else content)
                
            else:
                print("❌ 技能目录创建失败")
                
        else:
            print(f"❌ 技能创建失败: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_validation_module():
    """测试验证模块"""
    print("\n🧪 开始测试验证模块...")
    
    try:
        from skill_validator import skill_validator
        
        print("✅ 成功导入 skill_validator 模块")
        
        # 测试配置
        test_config = {
            "name": "test-skill",
            "description": "Test skill for validation. This is a test description that meets the minimum length requirement and includes keywords like trigger and scenarios.",
            "summary": "A test skill for validation",
            "steps": ["Step 1", "Step 2"],
            "input_desc": "User input",
            "output_desc": "Output result"
        }
        
        # 执行验证
        result = skill_validator.validate_skill_config(test_config)
        
        if result.is_valid:
            print("✅ 配置验证通过")
        else:
            print("⚠️ 配置验证发现问题:")
            for error in result.errors:
                print(f"   ❌ {error}")
        
        if result.warnings:
            print("⚠️ 验证警告:")
            for warning in result.warnings:
                print(f"   ⚠️ {warning}")
        
        if result.suggestions:
            print("💡 改进建议:")
            for suggestion in result.suggestions:
                print(f"   💡 {suggestion}")
                
    except Exception as e:
        print(f"❌ 验证模块测试失败: {e}")

def test_intelligent_recommender():
    """测试智能推荐模块"""
    print("\n🧪 开始测试智能推荐模块...")
    
    try:
        from intelligent_recommender import intelligent_recommender
        
        print("✅ 成功导入 intelligent_recommender 模块")
        
        # 测试用户描述
        user_description = "我想创建一个生成PDF报告的技能，可以处理数据并生成图表"
        
        # 测试类别推荐
        category, confidence = intelligent_recommender.recommend_category(user_description)
        print(f"✅ 推荐类别: {category} (置信度: {confidence:.2f})")
        
        # 测试名称推荐
        try:
            names = intelligent_recommender.recommend_names(category, user_description)
            print("✅ 推荐名称:")
            for i, name in enumerate(names, 1):
                print(f"   {i}. {name.name} - {name.reason} (置信度: {name.confidence:.2f})")
        except Exception as e:
            print(f"❌ 名称推荐失败: {e}")
            # 调试信息
            print(f"   类别: {category}")
            print(f"   可用模板: {list(intelligent_recommender.templates.keys())}")
        
        # 测试关键词推荐
        try:
            keywords = intelligent_recommender.recommend_keywords(category, user_description)
            print("✅ 推荐关键词:")
            print(f"   中文: {', '.join(keywords['chinese'][:5])}")
            print(f"   英文: {', '.join(keywords['english'][:5])}")
        except Exception as e:
            print(f"❌ 关键词推荐失败: {e}")
        
    except Exception as e:
        print(f"❌ 智能推荐模块测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始基础功能测试\n")
    
    # 测试基础创建功能
    test_basic_skill_creation()
    
    # 测试验证模块
    test_validation_module()
    
    # 测试智能推荐模块
    test_intelligent_recommender()
    
    print("\n🎉 基础功能测试完成!")
