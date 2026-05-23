"""Integration tests for the 'envdiff validate' CLI sub-command."""

import textwrap
from pathlib import Path

import pytest

from envdiff.cli import main


@pytest.fixture()
def good_env(tmp_path) -> str:
    p = tmp_path / "good.env"
    p.write_text("KEY=value\nANOTHER=123\n")
    return str(p)


@pytest.fixture()
def bad_env(tmp_path) -> str:
    p = tmp_path / "bad.env"
    p.write_text("MISSING_EQUALS\nKEY=\nKEY=dupe\n")
    return str(p)


def test_validate_good_file_exits_zero(good_env, capsys):
    code = main(["validate", good_env])
    assert code == 0
    out = capsys.readouterr().out
    assert "OK" in out


def test_validate_bad_file_exits_nonzero(bad_env, capsys):
    code = main(["validate", bad_env])
    assert code == 1
    out = capsys.readouterr().out
    assert "INVALID" in out


def test_validate_multiple_files(good_env, bad_env, capsys):
    code = main(["validate", good_env, bad_env])
    assert code == 1  # one bad file => non-zero
    out = capsys.readouterr().out
    assert "good.env" in out
    assert "bad.env" in out


def test_validate_no_color(bad_env, capsys):
    main(["validate", "--no-color", bad_env])
    out = capsys.readouterr().out
    # ANSI escape codes should not appear
    assert "\033[" not in out


def test_validate_nonexistent_file(capsys):
    code = main(["validate", "/no/such/file.env"])
    assert code == 1
    out = capsys.readouterr().out
    assert "INVALID" in out
