"""Integration tests for the --export / --output CLI flags."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.cli import main


@pytest.fixture()
def env_files(tmp_path: Path) -> tuple[Path, Path]:
    first = tmp_path / ".env.first"
    second = tmp_path / ".env.second"
    first.write_text("SHARED=hello\nONLY_FIRST=1\n")
    second.write_text("SHARED=world\nONLY_SECOND=2\n")
    return first, second


def test_export_json_stdout(env_files: tuple[Path, Path], capsys: pytest.CaptureFixture) -> None:
    first, second = env_files
    rc = main([str(first), str(second), "--export", "json"])
    assert rc == 1  # differences exist
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "missing_in_second" in data
    assert "mismatched" in data


def test_export_csv_stdout(env_files: tuple[Path, Path], capsys: pytest.CaptureFixture) -> None:
    first, second = env_files
    main([str(first), str(second), "--export", "csv"])
    captured = capsys.readouterr()
    assert "issue,key,value_first,value_second" in captured.out


def test_export_markdown_stdout(env_files: tuple[Path, Path], capsys: pytest.CaptureFixture) -> None:
    first, second = env_files
    main([str(first), str(second), "--export", "markdown"])
    captured = capsys.readouterr()
    assert "# envdiff Report" in captured.out


def test_export_to_file(env_files: tuple[Path, Path], tmp_path: Path) -> None:
    first, second = env_files
    out_file = tmp_path / "report.json"
    rc = main([str(first), str(second), "--export", "json", "--output", str(out_file)])
    assert rc == 1
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert "mismatched" in data


def test_output_without_export_is_error(env_files: tuple[Path, Path], tmp_path: Path) -> None:
    first, second = env_files
    with pytest.raises(SystemExit) as exc_info:
        main([str(first), str(second), "--output", str(tmp_path / "out.txt")])
    assert exc_info.value.code == 2


def test_no_differences_returns_zero(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    rc = main([str(f), str(f), "--export", "json"])
    assert rc == 0
