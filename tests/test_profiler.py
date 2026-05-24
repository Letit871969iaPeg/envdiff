"""Tests for envdiff.profiler."""
import pytest

from envdiff.profiler import profile_env_file, ProfileResult


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str):
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _write


def test_total_keys(tmp_env):
    path = tmp_env("a.env", "FOO=bar\nBAZ=qux\n")
    r = profile_env_file(path)
    assert r.total_keys == 2


def test_empty_env(tmp_env):
    path = tmp_env("empty.env", "# just a comment\n")
    r = profile_env_file(path)
    assert r.total_keys == 0
    assert r.avg_value_length == 0.0


def test_detects_duplicate_keys(tmp_env):
    path = tmp_env("dup.env", "FOO=first\nFOO=second\nBAR=baz\n")
    r = profile_env_file(path)
    assert "FOO" in r.duplicate_keys
    assert r.has_duplicates


def test_no_duplicates(tmp_env):
    path = tmp_env("nodup.env", "FOO=a\nBAR=b\n")
    r = profile_env_file(path)
    assert not r.has_duplicates


def test_empty_values_detected(tmp_env):
    path = tmp_env("emptyval.env", "FOO=\nBAR=hello\n")
    r = profile_env_file(path)
    assert "FOO" in r.empty_values
    assert r.has_empty_values


def test_no_empty_values(tmp_env):
    path = tmp_env("full.env", "FOO=bar\nBAZ=qux\n")
    r = profile_env_file(path)
    assert not r.has_empty_values


def test_longest_key(tmp_env):
    path = tmp_env("lk.env", "SHORT=x\nVERY_LONG_KEY_NAME=y\n")
    r = profile_env_file(path)
    assert r.longest_key[0] == "VERY_LONG_KEY_NAME"
    assert r.longest_key[1] == len("VERY_LONG_KEY_NAME")


def test_avg_value_length(tmp_env):
    path = tmp_env("avg.env", "A=12\nB=1234\n")  # lengths 2 and 4 -> avg 3.0
    r = profile_env_file(path)
    assert r.avg_value_length == 3.0


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        profile_env_file("/nonexistent/path/.env")
