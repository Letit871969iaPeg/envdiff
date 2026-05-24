"""Tests for envdiff.scanner."""

import pytest
from pathlib import Path

from envdiff.scanner import scan_for_env_files, ScanResult, _matches_patterns


@pytest.fixture()
def env_tree(tmp_path: Path) -> Path:
    """Create a small directory tree with various env-like files."""
    (tmp_path / ".env").write_text("A=1\n")
    (tmp_path / ".env.production").write_text("A=prod\n")
    (tmp_path / ".env.test").write_text("A=test\n")
    (tmp_path / "README.md").write_text("# readme\n")

    sub = tmp_path / "services" / "api"
    sub.mkdir(parents=True)
    (sub / ".env").write_text("B=2\n")
    (sub / "config.env").write_text("C=3\n")

    hidden = tmp_path / ".hidden_dir"
    hidden.mkdir()
    (hidden / ".env").write_text("SECRET=x\n")

    return tmp_path


def test_scan_finds_env_files(env_tree: Path) -> None:
    result = scan_for_env_files(env_tree)
    names = [p.name for p in result.found]
    assert ".env" in names
    assert ".env.production" in names
    assert ".env.test" in names


def test_scan_finds_nested_env(env_tree: Path) -> None:
    result = scan_for_env_files(env_tree)
    paths_str = [str(p) for p in result.found]
    assert any("services" in s for s in paths_str)


def test_scan_ignores_non_env_files(env_tree: Path) -> None:
    result = scan_for_env_files(env_tree)
    names = [p.name for p in result.found]
    assert "README.md" not in names


def test_scan_skips_hidden_dirs_by_default(env_tree: Path) -> None:
    result = scan_for_env_files(env_tree, skip_hidden_dirs=True)
    paths_str = [str(p) for p in result.found]
    assert not any(".hidden_dir" in s for s in paths_str)


def test_scan_includes_hidden_dirs_when_disabled(env_tree: Path) -> None:
    result = scan_for_env_files(env_tree, skip_hidden_dirs=False)
    paths_str = [str(p) for p in result.found]
    assert any(".hidden_dir" in s for s in paths_str)


def test_scan_result_counts(env_tree: Path) -> None:
    result = scan_for_env_files(env_tree)
    assert result.total_found >= 5
    assert result.total_skipped == 0


def test_scan_respects_max_depth(env_tree: Path) -> None:
    result_shallow = scan_for_env_files(env_tree, max_depth=1)
    result_deep = scan_for_env_files(env_tree, max_depth=5)
    assert result_shallow.total_found <= result_deep.total_found


def test_matches_patterns_dotenv() -> None:
    assert _matches_patterns(".env", (".env", ".env.*"))
    assert _matches_patterns(".env.local", (".env", ".env.*"))
    assert not _matches_patterns("settings.py", (".env", ".env.*"))


def test_scan_root_stored(env_tree: Path) -> None:
    result = scan_for_env_files(env_tree)
    assert result.root == env_tree.resolve()
