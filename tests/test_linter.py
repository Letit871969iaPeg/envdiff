"""Tests for envdiff.linter."""
import pytest
from pathlib import Path

from envdiff.linter import lint_env_file, lint_env_files, LintResult


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_clean_file_no_issues(tmp_env):
    path = tmp_env(".env", "APP_NAME=myapp\nDEBUG=false\n")
    result = lint_env_file(path)
    assert not result.has_issues()


def test_lowercase_key_warning(tmp_env):
    path = tmp_env(".env", "app_name=myapp\n")
    result = lint_env_file(path)
    assert result.has_issues()
    assert any("UPPER_SNAKE_CASE" in i.message for i in result.warnings())


def test_missing_separator_error(tmp_env):
    path = tmp_env(".env", "BADLINE\n")
    result = lint_env_file(path)
    errors = result.errors()
    assert any("separator" in e.message for e in errors)


def test_whitespace_around_eq_warning(tmp_env):
    path = tmp_env(".env", "KEY = value\n")
    result = lint_env_file(path)
    assert any("Whitespace around" in i.message for i in result.issues)


def test_value_trailing_whitespace_warning(tmp_env):
    path = tmp_env(".env", "KEY=value   \n")
    result = lint_env_file(path)
    assert any("whitespace" in i.message.lower() for i in result.warnings())


def test_comments_and_blanks_ignored(tmp_env):
    path = tmp_env(".env", "# comment\n\nVALID_KEY=ok\n")
    result = lint_env_file(path)
    assert not result.has_issues()


def test_file_not_found():
    result = lint_env_file("/nonexistent/.env")
    assert result.errors()
    assert "not found" in result.errors()[0].message.lower()


def test_lint_multiple_files(tmp_env):
    p1 = tmp_env("a.env", "GOOD=ok\n")
    p2 = tmp_env("b.env", "bad_key=value\n")
    results = lint_env_files([p1, p2])
    assert len(results) == 2
    assert not results[0].has_issues()
    assert results[1].has_issues()


def test_invalid_characters_in_key(tmp_env):
    path = tmp_env(".env", "123INVALID=value\n")
    result = lint_env_file(path)
    assert any("invalid characters" in i.message.lower() for i in result.errors())
