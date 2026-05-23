"""Tests for the env parser and comparator modules."""

import pytest
from pathlib import Path

from envdiff.parser import parse_env_file, _strip_quotes
from envdiff.comparator import compare_env_files


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def base_env(tmp_path: Path) -> Path:
    content = """
# Base env example
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY="supersecret"
DEBUG=true
"""
    f = tmp_path / ".env.example"
    f.write_text(content)
    return f


@pytest.fixture
def compare_env(tmp_path: Path) -> Path:
    content = """
DB_HOST=prod.db.example.com
DB_PORT=5432
SECRET_KEY='anothersecret'
EXTRA_KEY=surprise
"""
    f = tmp_path / ".env.production"
    f.write_text(content)
    return f


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

def test_parse_basic(base_env):
    result = parse_env_file(base_env)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["SECRET_KEY"] == "supersecret"  # quotes stripped
    assert result["DEBUG"] == "true"


def test_parse_ignores_comments_and_blanks(base_env):
    result = parse_env_file(base_env)
    assert all(not k.startswith("#") for k in result)


def test_parse_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "nonexistent.env")


def test_strip_quotes():
    assert _strip_quotes('"hello"') == "hello"
    assert _strip_quotes("'world'") == "world"
    assert _strip_quotes("plain") == "plain"
    assert _strip_quotes('"') == '"'  # single char, unchanged


# ---------------------------------------------------------------------------
# Comparator tests
# ---------------------------------------------------------------------------

def test_missing_in_compare(base_env, compare_env):
    result = compare_env_files(str(base_env), str(compare_env))
    assert "DEBUG" in result.missing_in_compare


def test_missing_in_base(base_env, compare_env):
    result = compare_env_files(str(base_env), str(compare_env))
    assert "EXTRA_KEY" in result.missing_in_base


def test_value_mismatch_detected(base_env, compare_env):
    result = compare_env_files(str(base_env), str(compare_env), check_values=True)
    assert "DB_HOST" in result.value_mismatches
    assert "SECRET_KEY" in result.value_mismatches


def test_no_value_mismatch_without_flag(base_env, compare_env):
    result = compare_env_files(str(base_env), str(compare_env), check_values=False)
    assert result.value_mismatches == {}


def test_has_differences(base_env, compare_env):
    result = compare_env_files(str(base_env), str(compare_env))
    assert result.has_differences is True


def test_no_differences_identical(tmp_path):
    content = "FOO=bar\nBAZ=qux\n"
    f1 = tmp_path / ".env.a"
    f2 = tmp_path / ".env.b"
    f1.write_text(content)
    f2.write_text(content)
    result = compare_env_files(str(f1), str(f2), check_values=True)
    assert not result.has_differences
