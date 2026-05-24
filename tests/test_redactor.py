"""Tests for envdiff.redactor."""

import pytest
from envdiff.redactor import (
    RedactResult,
    is_sensitive_key,
    redact_env,
    REDACT_PLACEHOLDER,
)


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "SECRET_TOKEN": "tok_xyz",
        "PORT": "8080",
        "DATABASE_URL": "postgres://user:pass@host/db",
    }


def test_is_sensitive_key_detects_password():
    assert is_sensitive_key("DB_PASSWORD") is True


def test_is_sensitive_key_detects_api_key():
    assert is_sensitive_key("API_KEY") is True


def test_is_sensitive_key_detects_secret():
    assert is_sensitive_key("SECRET_TOKEN") is True


def test_is_sensitive_key_safe_key():
    assert is_sensitive_key("APP_NAME") is False
    assert is_sensitive_key("PORT") is False
    assert is_sensitive_key("DEBUG") is False


def test_redact_env_replaces_sensitive_values(sample_env):
    result = redact_env(sample_env)
    assert result.redacted["DB_PASSWORD"] == REDACT_PLACEHOLDER
    assert result.redacted["API_KEY"] == REDACT_PLACEHOLDER
    assert result.redacted["SECRET_TOKEN"] == REDACT_PLACEHOLDER
    assert result.redacted["DATABASE_URL"] == REDACT_PLACEHOLDER


def test_redact_env_preserves_safe_values(sample_env):
    result = redact_env(sample_env)
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["DEBUG"] == "true"
    assert result.redacted["PORT"] == "8080"


def test_redact_result_counts(sample_env):
    result = redact_env(sample_env)
    assert result.redact_count == 4
    assert len(result.redacted_keys) == 4


def test_redact_original_unchanged(sample_env):
    result = redact_env(sample_env)
    assert result.original["DB_PASSWORD"] == "s3cr3t"


def test_redact_extra_patterns(sample_env):
    result = redact_env(sample_env, extra_patterns=[r"debug"])
    assert result.redacted["DEBUG"] == REDACT_PLACEHOLDER


def test_redact_invalid_extra_pattern_ignored(sample_env):
    # Should not raise; bad pattern is skipped
    result = redact_env(sample_env, extra_patterns=[r"[invalid"])
    assert result.redact_count == 4


def test_redact_empty_env():
    result = redact_env({})
    assert result.redact_count == 0
    assert result.redacted == {}
