#!/usr/bin/env python3
"""
create_skill.py

用途：根据收集好的技能信息，自动创建完整的 Skill 文件包目录结构。
输入：通过命令行参数或交互模式传入技能配置（JSON 格式）
输出：在指定路径创建完整的 Skill 文件夹

用法：
  python scripts/create_skill.py --config '{"name":"my-skill",...}' --output .claude/skills/
  python scripts/create_skill.py --config-file skill_config.json --output ./
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime


def create_skill_structure(config: dict, output_dir: str) -> dict:
    """
    根据配置创建技能文件包。
    
    config 字段说明：
      name         str   技能名称（小写+连字符）
      description  str   触发描述
      summary      str   一句话简介
      dependencies list  依赖库列表
      platforms    list  适用平台
      input_desc   str   输入格式描述
      output_desc  str   输出格式描述
      steps        list  执行步骤列表
      notes        list  注意事项列表
      has_scripts  bool  是否创建 scripts/ 目录
      has_refs     bool  是否创建 references/ 目录
      has_assets   bool  是否创建 assets/ 目录
      has_evals    bool  是否创建 evals/ 目录
    
    返回：
      {"success": True, "path": "...", "files_created": [...]}
    """
    name = config.get("name", "my-skill")
    skill_dir = Path(output_dir) / name

    if skill_dir.exists():
        return {
            "success": False,
            "error": f"目录已存在：{skill_dir}\n请先删除或换一个名称。"
        }

    created_files = []

    # ── 创建根目录 ──────────────────────────────────────
    skill_dir.mkdir(parents=True)

    # ── SKILL.md ────────────────────────────────────────
    skill_md = _build_skill_md(config)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    created_files.append("SKILL.md")

    # ── README.md ───────────────────────────────────────
    readme = _build_readme(config)
    (skill_dir / "README.md").write_text(readme, encoding="utf-8")
    created_files.append("README.md")

    # ── scripts/ ────────────────────────────────────────
    if config.get("has_scripts"):
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "__init__.py").write_text("", encoding="utf-8")
        main_py = _build_main_script(config)
        (scripts_dir / "main.py").write_text(main_py, encoding="utf-8")
        created_files += ["scripts/__init__.py", "scripts/main.py"]

    # ── references/ ─────────────────────────────────────
    if config.get("has_refs"):
        refs_dir = skill_dir / "references"
        refs_dir.mkdir()
        guide = _build_reference_guide(config)
        (refs_dir / "guide.md").write_text(guide, encoding="utf-8")
        created_files.append("references/guide.md")

    # ── assets/ ─────────────────────────────────────────
    if config.get("has_assets"):
        assets_dir = skill_dir / "assets"
        assets_dir.mkdir()
        (assets_dir / ".gitkeep").write_text(
            "# 将模板/素材文件放在这里\n", encoding="utf-8"
        )
        created_files.append("assets/  (空目录，请手动添加素材)")

    # ── evals/ ──────────────────────────────────────────
    if config.get("has_evals"):
        evals_dir = skill_dir / "evals" / "files"
        evals_dir.mkdir(parents=True)
        evals_json = _build_evals(config)
        (skill_dir / "evals" / "evals.json").write_text(
            json.dumps(evals_json, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        created_files.append("evals/evals.json")

    return {
        "success": True,
        "path": str(skill_dir.resolve()),
        "files_created": created_files
    }


# ── 文件内容构建函数 ──────────────────────────────────────

def _build_skill_md(c: dict) -> str:
    name = c.get("name", "my-skill")
    description = c.get("description", "请填写触发描述")
    summary = c.get("summary", "")
    deps = c.get("dependencies", [])
    platforms = c.get("platforms", ["claude-code", "claude-ai"])
    input_desc = c.get("input_desc", "用户提供需求描述")
    output_desc = c.get("output_desc", "处理结果")
    steps = c.get("steps", ["执行任务"])
    notes = c.get("notes", [])

    lines = ["---", f"name: {name}", "description: |"]
    for line in description.strip().split("\n"):
        lines.append(f"  {line}")

    if deps:
        lines.append("compatibility:")
        lines.append(f"  dependencies: [{', '.join(deps)}]")
        lines.append(f"  platforms: [{', '.join(platforms)}]")

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


def _build_readme(c: dict) -> str:
    name = c.get("name", "my-skill")
    summary = c.get("summary", "")
    deps = c.get("dependencies", [])
    today = datetime.now().strftime("%Y-%m-%d")

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
*生成于 {today}*
"""


def _build_main_script(c: dict) -> str:
    name = c.get("name", "my-skill")
    return f'''#!/usr/bin/env python3
"""
{name} - 主执行脚本

用途：[描述这个脚本做什么]
输入：[描述输入参数]
输出：[描述输出结果]

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
    # TODO: 在这里实现核心逻辑
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


def _build_reference_guide(c: dict) -> str:
    name = c.get("name", "my-skill")
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


def _build_evals(c: dict) -> dict:
    name = c.get("name", "my-skill")
    summary = c.get("summary", "执行任务")
    return {
        "skill_name": name,
        "evals": [
            {
                "id": 1,
                "prompt": f"请帮我{summary}",
                "expected_output": f"成功完成{summary}，并提供结果",
                "files": [],
                "expectations": [
                    "输出包含完整结果",
                    "没有报错信息"
                ]
            }
        ]
    }


# ── 主入口 ────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="创建 Agent Skill 文件包",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--config", type=str, help="JSON 格式的技能配置（字符串）")
    parser.add_argument("--config-file", type=str, help="JSON 配置文件路径")
    parser.add_argument("--output", type=str, default=".", help="输出目录（默认当前目录）")

    args = parser.parse_args()

    if args.config_file:
        with open(args.config_file, encoding="utf-8") as f:
            config = json.load(f)
    elif args.config:
        config = json.loads(args.config)
    else:
        print("错误：请提供 --config 或 --config-file", file=sys.stderr)
        sys.exit(1)

    result = create_skill_structure(config, args.output)

    if result["success"]:
        print(f"\n✅ 技能包创建成功！")
        print(f"   路径：{result['path']}")
        print(f"\n   创建的文件：")
        for f in result["files_created"]:
            print(f"   ├── {f}")
    else:
        print(f"\n❌ 创建失败：{result['error']}", file=sys.stderr)
        sys.exit(1)
