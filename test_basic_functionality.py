"""Tests for basic skill-generator functionality."""

import pytest
from pathlib import Path

from create_skill import create_skill_structure
from skill_validator import skill_validator
from intelligent_recommender import intelligent_recommender


VALID_CONFIG = {
    "name": "test-skill",
    "description": (
        "Test skill for validation. This is a test description that meets "
        "the minimum length requirement and includes keywords like "
        "trigger and scenarios."
    ),
    "summary": "A test skill for validation",
    "steps": [
        "Read user input and validate format",
        "Process the data according to requirements",
        "Generate output and save results",
    ],
    "input_desc": "User provides text input for processing",
    "output_desc": "Processed results and summary report",
}


class TestSkillCreation:
    """Tests for the create_skill module."""

    def test_creates_skill_directory(self, tmp_path):
        result = create_skill_structure(VALID_CONFIG, str(tmp_path))
        assert result["success"] is True
        assert Path(result["path"]).exists()

    def test_creates_required_files(self, tmp_path):
        result = create_skill_structure(VALID_CONFIG, str(tmp_path))
        skill_dir = tmp_path / "test-skill"
        assert (skill_dir / "SKILL.md").exists()
        assert (skill_dir / "README.md").exists()

    def test_skill_md_contains_name(self, tmp_path):
        create_skill_structure(VALID_CONFIG, str(tmp_path))
        content = (tmp_path / "test-skill" / "SKILL.md").read_text(encoding="utf-8")
        assert "name: test-skill" in content

    def test_skill_md_contains_description(self, tmp_path):
        create_skill_structure(VALID_CONFIG, str(tmp_path))
        content = (tmp_path / "test-skill" / "SKILL.md").read_text(encoding="utf-8")
        assert "Test skill for validation" in content

    def test_skill_md_contains_steps(self, tmp_path):
        create_skill_structure(VALID_CONFIG, str(tmp_path))
        content = (tmp_path / "test-skill" / "SKILL.md").read_text(encoding="utf-8")
        assert "Read user input and validate format" in content

    def test_fails_on_duplicate_directory(self, tmp_path):
        create_skill_structure(VALID_CONFIG, str(tmp_path))
        result = create_skill_structure(VALID_CONFIG, str(tmp_path))
        assert result["success"] is False
        assert "已存在" in result["error"]

    def test_creates_scripts_directory(self, tmp_path):
        config = {**VALID_CONFIG, "has_scripts": True}
        result = create_skill_structure(config, str(tmp_path))
        assert result["success"] is True
        assert (tmp_path / "test-skill" / "scripts" / "__init__.py").exists()
        assert (tmp_path / "test-skill" / "scripts" / "main.py").exists()

    def test_creates_references_directory(self, tmp_path):
        config = {**VALID_CONFIG, "has_refs": True}
        result = create_skill_structure(config, str(tmp_path))
        assert result["success"] is True
        assert (tmp_path / "test-skill" / "references" / "guide.md").exists()

    def test_creates_assets_directory(self, tmp_path):
        config = {**VALID_CONFIG, "has_assets": True}
        result = create_skill_structure(config, str(tmp_path))
        assert result["success"] is True
        assert (tmp_path / "test-skill" / "assets").exists()

    def test_creates_evals_directory(self, tmp_path):
        config = {**VALID_CONFIG, "has_evals": True}
        result = create_skill_structure(config, str(tmp_path))
        assert result["success"] is True
        assert (tmp_path / "test-skill" / "evals" / "evals.json").exists()

    def test_files_created_list(self, tmp_path):
        result = create_skill_structure(VALID_CONFIG, str(tmp_path))
        assert "SKILL.md" in result["files_created"]
        assert "README.md" in result["files_created"]


class TestSkillValidator:
    """Tests for the skill_validator module."""

    def test_valid_config_passes(self):
        result = skill_validator.validate_skill_config(VALID_CONFIG)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_missing_name_fails(self):
        config = {**VALID_CONFIG}
        del config["name"]
        result = skill_validator.validate_skill_config(config)
        assert result.is_valid is False

    def test_missing_description_fails(self):
        config = {**VALID_CONFIG}
        del config["description"]
        result = skill_validator.validate_skill_config(config)
        assert result.is_valid is False

    def test_short_description_fails(self):
        config = {**VALID_CONFIG, "description": "too short"}
        result = skill_validator.validate_skill_config(config)
        assert result.is_valid is False

    def test_invalid_name_format_fails(self):
        config = {**VALID_CONFIG, "name": "Invalid Name"}
        result = skill_validator.validate_skill_config(config)
        assert result.is_valid is False

    def test_suggestions_provided(self):
        result = skill_validator.validate_skill_config(VALID_CONFIG)
        assert isinstance(result.suggestions, list)

    def test_warnings_provided(self):
        result = skill_validator.validate_skill_config(VALID_CONFIG)
        assert isinstance(result.warnings, list)

    def test_validation_report_generated(self):
        result = skill_validator.validate_skill_config(VALID_CONFIG)
        report = skill_validator.generate_validation_report(result, "test-skill")
        assert "test-skill" in report
        assert "验证报告" in report


class TestIntelligentRecommender:
    """Tests for the intelligent_recommender module."""

    def test_recommend_category(self):
        description = "我想创建一个生成PDF报告的技能，可以处理数据并生成图表"
        category, confidence = intelligent_recommender.recommend_category(description)
        assert isinstance(category, str)
        assert 0 <= confidence <= 1

    def test_recommend_names(self):
        description = "我想创建一个生成PDF报告的技能"
        category, _ = intelligent_recommender.recommend_category(description)
        names = intelligent_recommender.recommend_names(category, description)
        assert len(names) > 0
        for name in names:
            assert hasattr(name, "name")
            assert hasattr(name, "reason")
            assert hasattr(name, "confidence")

    def test_recommend_keywords(self):
        description = "我想创建一个生成PDF报告的技能"
        category, _ = intelligent_recommender.recommend_category(description)
        keywords = intelligent_recommender.recommend_keywords(category, description)
        assert "chinese" in keywords
        assert "english" in keywords
        assert len(keywords["chinese"]) > 0
        assert len(keywords["english"]) > 0

    def test_generate_description(self):
        description = "生成PDF文档"
        category, _ = intelligent_recommender.recommend_category(description)
        result = intelligent_recommender.generate_description(
            category, description, "pdf-creator"
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_recommend_dependencies(self):
        description = "生成PDF文档"
        category, _ = intelligent_recommender.recommend_category(description)
        deps = intelligent_recommender.recommend_dependencies(category, description)
        assert isinstance(deps, list)
