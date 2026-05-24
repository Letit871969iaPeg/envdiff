"""Tests for envdiff.grouper."""

import pytest

from envdiff.grouper import GroupResult, group_env_files, group_env_keys


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_ACCESS_KEY": "AKIA…",
        "AWS_SECRET_KEY": "secret",
        "PORT": "8080",
        "DEBUG": "true",
    }


def test_group_creates_prefix_groups(sample_env):
    result = group_env_keys(sample_env)
    assert "DB" in result.groups
    assert "AWS" in result.groups
    assert sorted(result.groups["DB"]) == ["DB_HOST", "DB_NAME", "DB_PORT"]
    assert sorted(result.groups["AWS"]) == ["AWS_ACCESS_KEY", "AWS_SECRET_KEY"]


def test_keys_without_separator_are_ungrouped(sample_env):
    result = group_env_keys(sample_env)
    assert "PORT" in result.ungrouped
    assert "DEBUG" in result.ungrouped


def test_total_keys_matches_input(sample_env):
    result = group_env_keys(sample_env)
    assert result.total_keys == len(sample_env)


def test_group_names_are_sorted(sample_env):
    result = group_env_keys(sample_env)
    assert result.group_names == sorted(result.group_names)


def test_largest_group(sample_env):
    result = group_env_keys(sample_env)
    name, size = result.largest_group()
    assert name == "DB"
    assert size == 3


def test_largest_group_empty_env():
    result = group_env_keys({})
    name, size = result.largest_group()
    assert name == ""
    assert size == 0


def test_min_group_size_moves_small_groups_to_ungrouped():
    env = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SOLO_KEY": "value",  # prefix SOLO has only 1 member
    }
    result = group_env_keys(env, min_group_size=2)
    assert "DB" in result.groups
    assert "SOLO" not in result.groups
    assert "SOLO_KEY" in result.ungrouped


def test_custom_separator():
    env = {
        "DB.HOST": "localhost",
        "DB.PORT": "5432",
        "PLAIN": "value",
    }
    result = group_env_keys(env, separator=".")
    assert "DB" in result.groups
    assert "PLAIN" in result.ungrouped


def test_group_env_files_returns_per_file_results():
    envs = {
        "development": {"DB_HOST": "localhost", "DB_PORT": "5432", "PORT": "8080"},
        "production": {"DB_HOST": "prod-db", "DB_PORT": "5432", "PORT": "80"},
    }
    results = group_env_files(envs)
    assert set(results.keys()) == {"development", "production"}
    for name, res in results.items():
        assert isinstance(res, GroupResult)
        assert "DB" in res.groups
        assert "PORT" in res.ungrouped
