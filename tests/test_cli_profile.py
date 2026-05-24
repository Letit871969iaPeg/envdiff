"""CLI integration tests for the `profile` sub-command."""
import json
import pytest
from click.testing import CliRunner

from envdiff.cli import main


@pytest.fixture()
def env_files(tmp_path):
    a = tmp_path / "a.env"
    a.write_text("FOO=bar\nSECRET=abc\nEMPTY=\n", encoding="utf-8")
    b = tmp_path / "b.env"
    b.write_text("FOO=baz\nFOO=dup\nDB_HOST=localhost\n", encoding="utf-8")
    return str(a), str(b)


def test_profile_exits_zero(env_files):
    runner = CliRunner()
    result = runner.invoke(main, ["profile", env_files[0]])
    assert result.exit_code == 0


def test_profile_shows_total_keys(env_files):
    runner = CliRunner()
    result = runner.invoke(main, ["profile", env_files[0]])
    assert "Total keys" in result.output


def test_profile_reports_empty_value(env_files):
    runner = CliRunner()
    result = runner.invoke(main, ["profile", env_files[0]])
    assert "EMPTY" in result.output


def test_profile_reports_duplicate(env_files):
    runner = CliRunner()
    result = runner.invoke(main, ["profile", env_files[1]])
    assert "FOO" in result.output


def test_profile_multiple_files(env_files):
    runner = CliRunner()
    result = runner.invoke(main, ["profile", env_files[0], env_files[1]])
    assert result.exit_code == 0
    assert result.output.count("Profile:") == 2


def test_profile_missing_file_exits_nonzero(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["profile", str(tmp_path / "missing.env")])
    assert result.exit_code != 0
