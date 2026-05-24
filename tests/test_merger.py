"""Tests for envdiff.merger."""

from __future__ import annotations

import os
import textwrap

import pytest

from envdiff.merger import MergeResult, merge_env_files, render_merged_template


@pytest.fixture()
def env_a(tmp_path):
    p = tmp_path / "a.env"
    p.write_text(textwrap.dedent("""\
        APP_NAME=myapp
        DEBUG=true
        SECRET_KEY=abc123
    """))
    return str(p)


@pytest.fixture()
def env_b(tmp_path):
    p = tmp_path / "b.env"
    p.write_text(textwrap.dedent("""\
        APP_NAME=myapp-prod
        DATABASE_URL=postgres://localhost/db
    """))
    return str(p)


def test_merge_collects_all_keys(env_a, env_b):
    result = merge_env_files([env_a, env_b])
    assert result.all_keys == {"APP_NAME", "DEBUG", "SECRET_KEY", "DATABASE_URL"}


def test_merge_last_strategy(env_a, env_b):
    result = merge_env_files([env_a, env_b], strategy="last")
    assert result.keys["APP_NAME"] == "myapp-prod"


def test_merge_first_strategy(env_a, env_b):
    result = merge_env_files([env_a, env_b], strategy="first")
    assert result.keys["APP_NAME"] == "myapp"


def test_merge_sources_provenance(env_a, env_b):
    result = merge_env_files([env_a, env_b])
    assert env_a in result.sources["DEBUG"]
    assert env_b not in result.sources["DEBUG"]
    assert env_b in result.sources["DATABASE_URL"]


def test_files_missing_key(env_a, env_b):
    result = merge_env_files([env_a, env_b])
    missing = result.files_missing_key("DATABASE_URL")
    assert env_a in missing
    assert env_b not in missing


def test_invalid_strategy_raises(env_a):
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_env_files([env_a], strategy="newest")


def test_render_template_contains_all_keys(env_a, env_b):
    result = merge_env_files([env_a, env_b])
    template = render_merged_template(result)
    for key in result.all_keys:
        assert key in template


def test_render_template_warns_missing(env_a, env_b):
    result = merge_env_files([env_a, env_b])
    template = render_merged_template(result)
    assert "# WARNING" in template


def test_render_template_no_warnings_when_universal(env_a):
    # single file — every key is in all files
    result = merge_env_files([env_a])
    template = render_merged_template(result)
    assert "# WARNING" not in template
