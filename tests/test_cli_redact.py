"""Integration tests for the redact subcommand via CLI."""

import os
import pytest
from click.testing import CliRunner
from envdiff.cli import main


@pytest.fixture
def env_files(tmp_path):
    f = tmp_path / ".env"
    f.write_text(
        "APP_NAME=myapp\n"
        "DB_PASSWORD=s3cr3t\n"
        "API_KEY=abc123\n"
        "DEBUG=true\n"
        "PORT=8080\n"
    )
    return {"env": str(f)}


def test_redact_exits_zero(env_files):
    runner = CliRunner()
    result = runner.invoke(main, ["redact", env_files["env"]])
    assert result.exit_code == 0


def test_redact_output_shows_redacted_keys(env_files):
    runner = CliRunner()
    result = runner.invoke(main, ["redact", env_files["env"]])
    assert "DB_PASSWORD" in result.output
    assert "API_KEY" in result.output


def test_redact_output_does_not_show_secret_values(env_files):
    runner = CliRunner()
    result = runner.invoke(main, ["redact", env_files["env"]])
    assert "s3cr3t" not in result.output
    assert "abc123" not in result.output


def test_redact_safe_keys_not_flagged(env_files):
    runner = CliRunner()
    result = runner.invoke(main, ["redact", env_files["env"]])
    # Safe keys should not appear in the redacted-keys list
    # The report lists only redacted keys under the summary section
    assert "PORT" not in result.output or "REDACTED" not in result.output


def test_redact_extra_pattern(env_files):
    runner = CliRunner()
    result = runner.invoke(
        main, ["redact", "--pattern", "debug", env_files["env"]]
    )
    assert result.exit_code == 0
    assert "DEBUG" in result.output


def test_redact_missing_file():
    runner = CliRunner()
    result = runner.invoke(main, ["redact", "/nonexistent/.env"])
    assert result.exit_code != 0
