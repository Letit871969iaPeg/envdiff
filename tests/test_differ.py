"""Tests for envdiff.differ and envdiff.diff_exporter."""
from __future__ import annotations

import json
import os
import textwrap

import pytest

from envdiff.differ import diff_env_files, EnvDiff, DiffLine
from envdiff.diff_exporter import export_diff


@pytest.fixture()
def env_left(tmp_path):
    p = tmp_path / "left.env"
    p.write_text(textwrap.dedent("""\
        APP_NAME=myapp
        DEBUG=true
        SECRET=old_secret
        ONLY_LEFT=yes
    """))
    return str(p)


@pytest.fixture()
def env_right(tmp_path):
    p = tmp_path / "right.env"
    p.write_text(textwrap.dedent("""\
        APP_NAME=myapp
        DEBUG=false
        SECRET=new_secret
        ONLY_RIGHT=yes
    """))
    return str(p)


def test_diff_detects_unchanged(env_left, env_right):
    diff = diff_env_files(env_left, env_right)
    assert any(l.kind == "unchanged" and l.key == "APP_NAME" for l in diff.lines)


def test_diff_detects_changed(env_left, env_right):
    diff = diff_env_files(env_left, env_right)
    changed_keys = {l.key for l in diff.changed}
    assert "DEBUG" in changed_keys
    assert "SECRET" in changed_keys


def test_diff_detects_removed(env_left, env_right):
    diff = diff_env_files(env_left, env_right)
    assert any(l.key == "ONLY_LEFT" and l.kind == "removed" for l in diff.lines)


def test_diff_detects_added(env_left, env_right):
    diff = diff_env_files(env_left, env_right)
    assert any(l.key == "ONLY_RIGHT" and l.kind == "added" for l in diff.lines)


def test_identical_files(tmp_path):
    content = "KEY=value\nOTHER=123\n"
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text(content)
    b.write_text(content)
    diff = diff_env_files(str(a), str(b))
    assert diff.is_identical()


def test_export_json(env_left, env_right):
    import io
    diff = diff_env_files(env_left, env_right)
    buf = io.StringIO()
    export_diff(diff, "json", buf)
    data = json.loads(buf.getvalue())
    assert "lines" in data
    assert data["identical"] is False
    assert any(l["key"] == "APP_NAME" for l in data["lines"])


def test_export_csv(env_left, env_right):
    import io
    diff = diff_env_files(env_left, env_right)
    buf = io.StringIO()
    export_diff(diff, "csv", buf)
    text = buf.getvalue()
    assert text.startswith("kind,key,left_value,right_value")
    assert "DEBUG" in text


def test_export_markdown(env_left, env_right):
    import io
    diff = diff_env_files(env_left, env_right)
    buf = io.StringIO()
    export_diff(diff, "markdown", buf)
    text = buf.getvalue()
    assert "## Diff" in text
    assert "| Kind |" in text


def test_export_invalid_format(env_left, env_right):
    import io
    diff = diff_env_files(env_left, env_right)
    with pytest.raises(ValueError, match="Unsupported format"):
        export_diff(diff, "xml", io.StringIO())
