"""Tests for envdiff.validator."""

import textwrap
from pathlib import Path

import pytest

from envdiff.validator import validate_env_file, ValidationIssue


@pytest.fixture()
def tmp_env(tmp_path):
    """Factory that writes content to a temp .env file and returns its path."""

    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content))
        return str(p)

    return _write


def test_valid_file(tmp_env):
    path = tmp_env("""
        # comment
        KEY=value
        ANOTHER=123
    """)
    result = validate_env_file(path)
    assert result.is_valid
    assert not result.issues


def test_missing_separator(tmp_env):
    path = tmp_env("BADLINE\n")
    result = validate_env_file(path)
    assert result.has_errors
    issues = [i for i in result.issues if i.severity == "error"]
    assert any("separator" in i.message for i in issues)


def test_empty_value_warning(tmp_env):
    path = tmp_env("KEY=\n")
    result = validate_env_file(path)
    assert not result.has_errors
    assert result.has_warnings
    assert any("Empty value" in i.message for i in result.issues)


def test_duplicate_key_warning(tmp_env):
    path = tmp_env("KEY=a\nKEY=b\n")
    result = validate_env_file(path)
    assert not result.has_errors
    assert any("Duplicate" in i.message for i in result.issues)


def test_file_not_found():
    result = validate_env_file("/nonexistent/.env")
    assert result.has_errors
    assert any("not found" in i.message for i in result.issues)


def test_empty_key(tmp_env):
    path = tmp_env("=value\n")
    result = validate_env_file(path)
    errors = [i for i in result.issues if i.severity == "error"]
    assert any("Empty key" in i.message for i in errors)


def test_str_representation():
    issue = ValidationIssue(line_number=3, key="FOO", message="Empty value", severity="warning")
    text = str(issue)
    assert "WARNING" in text
    assert "FOO" in text
    assert "3" in text
