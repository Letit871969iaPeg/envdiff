"""Integration tests for the `diff` subcommand in the CLI."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.cli import main


@pytest.fixture()
def env_files(tmp_path):
    left = tmp_path / "left.env"
    right = tmp_path / "right.env"
    left.write_text(textwrap.dedent("""\
        SHARED=same
        CHANGED=old
        ONLY_LEFT=yes
    """))
    right.write_text(textwrap.dedent("""\
        SHARED=same
        CHANGED=new
        ONLY_RIGHT=yes
    """))
    return str(left), str(right)


def test_diff_exits_zero_when_differences(env_files):
    runner = CliRunner()
    left, right = env_files
    result = runner.invoke(main, ["diff", left, right])
    # non-zero because files differ
    assert result.exit_code == 1


def test_diff_exits_zero_for_identical(tmp_path):
    p = tmp_path / "a.env"
    p.write_text("KEY=val\n")
    runner = CliRunner()
    result = runner.invoke(main, ["diff", str(p), str(p)])
    assert result.exit_code == 0
    assert "identical" in result.output.lower()


def test_diff_output_contains_keys(env_files):
    runner = CliRunner()
    left, right = env_files
    result = runner.invoke(main, ["diff", left, right])
    assert "CHANGED" in result.output
    assert "ONLY_LEFT" in result.output
    assert "ONLY_RIGHT" in result.output


def test_diff_export_json_stdout(env_files):
    runner = CliRunner()
    left, right = env_files
    result = runner.invoke(main, ["diff", "--format", "json", left, right])
    data = json.loads(result.output)
    assert "lines" in data
    assert data["identical"] is False


def test_diff_export_to_file(env_files, tmp_path):
    runner = CliRunner()
    left, right = env_files
    out = tmp_path / "diff.json"
    result = runner.invoke(main, ["diff", "--format", "json", "--output", str(out), left, right])
    assert out.exists()
    data = json.loads(out.read_text())
    assert "lines" in data
