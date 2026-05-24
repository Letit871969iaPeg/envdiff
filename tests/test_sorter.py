"""Tests for envdiff.sorter."""

import pytest

from envdiff.sorter import analyze_sort, sort_env_files, SortResult


@pytest.fixture
def sorted_env():
    return {"ALPHA": "1", "BETA": "2", "GAMMA": "3"}


@pytest.fixture
def unsorted_env():
    return {"GAMMA": "3", "ALPHA": "1", "BETA": "2"}


# ---------------------------------------------------------------------------
# analyze_sort
# ---------------------------------------------------------------------------

def test_sorted_env_is_detected(sorted_env):
    result = analyze_sort(sorted_env, path=".env")
    assert result.is_sorted is True
    assert result.out_of_order == []


def test_unsorted_env_is_detected(unsorted_env):
    result = analyze_sort(unsorted_env, path=".env")
    assert result.is_sorted is False
    assert len(result.out_of_order) > 0


def test_sorted_keys_are_alphabetical(unsorted_env):
    result = analyze_sort(unsorted_env)
    keys_in_output = [line.split("=")[0] for line in result.sorted_keys]
    assert keys_in_output == sorted(unsorted_env.keys(), key=str.lower)


def test_out_of_order_contains_tuples(unsorted_env):
    result = analyze_sort(unsorted_env)
    for item in result.out_of_order:
        assert len(item) == 3  # (index, original_key, expected_key)


def test_empty_env_is_sorted():
    result = analyze_sort({})
    assert result.is_sorted is True
    assert result.sorted_keys == []


def test_single_key_env_is_sorted():
    result = analyze_sort({"ONLY": "value"})
    assert result.is_sorted is True


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------

def test_render_includes_comment(sorted_env):
    result = analyze_sort(sorted_env, path=".env.example")
    rendered = result.render(comment=True)
    assert "# Sorted by envdiff" in rendered
    assert ".env.example" in rendered


def test_render_without_comment(sorted_env):
    result = analyze_sort(sorted_env)
    rendered = result.render(comment=False)
    assert rendered.startswith("ALPHA=")


def test_render_ends_with_newline(sorted_env):
    result = analyze_sort(sorted_env)
    assert result.render().endswith("\n")


# ---------------------------------------------------------------------------
# sort_env_files
# ---------------------------------------------------------------------------

def test_sort_env_files_returns_all_paths(sorted_env, unsorted_env):
    files = {".env.sorted": sorted_env, ".env.unsorted": unsorted_env}
    results = sort_env_files(files)
    assert set(results.keys()) == {".env.sorted", ".env.unsorted"}


def test_sort_env_files_correct_types(sorted_env, unsorted_env):
    results = sort_env_files({".env": sorted_env})
    assert isinstance(results[".env"], SortResult)


def test_sort_env_files_path_propagated(sorted_env):
    results = sort_env_files({".env.prod": sorted_env})
    assert results[".env.prod"].path == ".env.prod"
