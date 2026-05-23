"""Tests for envdiff.exporter — JSON, CSV, and Markdown export."""

from __future__ import annotations

import csv
import io
import json

import pytest

from envdiff.comparator import EnvDiffResult
from envdiff.exporter import export_result


@pytest.fixture()
def sample_result() -> EnvDiffResult:
    return EnvDiffResult(
        missing_in_second={"ONLY_IN_FIRST"},
        missing_in_first={"ONLY_IN_SECOND"},
        mismatched={"SHARED_KEY": ("value_a", "value_b")},
    )


@pytest.fixture()
def empty_result() -> EnvDiffResult:
    return EnvDiffResult(missing_in_second=set(), missing_in_first=set(), mismatched={})


# ── JSON ──────────────────────────────────────────────────────────────────────


def test_json_structure(sample_result: EnvDiffResult) -> None:
    text = export_result(sample_result, "json")
    data = json.loads(text)
    assert set(data["missing_in_second"]) == {"ONLY_IN_FIRST"}
    assert set(data["missing_in_first"]) == {"ONLY_IN_SECOND"}
    assert len(data["mismatched"]) == 1
    entry = data["mismatched"][0]
    assert entry["key"] == "SHARED_KEY"
    assert entry["first"] == "value_a"
    assert entry["second"] == "value_b"


def test_json_empty(empty_result: EnvDiffResult) -> None:
    data = json.loads(export_result(empty_result, "json"))
    assert data == {"missing_in_second": [], "missing_in_first": [], "mismatched": []}


# ── CSV ───────────────────────────────────────────────────────────────────────


def test_csv_has_header(sample_result: EnvDiffResult) -> None:
    text = export_result(sample_result, "csv")
    reader = csv.DictReader(io.StringIO(text))
    assert reader.fieldnames == ["issue", "key", "value_first", "value_second"]


def test_csv_rows(sample_result: EnvDiffResult) -> None:
    text = export_result(sample_result, "csv")
    rows = list(csv.DictReader(io.StringIO(text)))
    issues = {r["issue"] for r in rows}
    assert issues == {"missing_in_second", "missing_in_first", "mismatched"}


def test_csv_empty(empty_result: EnvDiffResult) -> None:
    text = export_result(empty_result, "csv")
    rows = list(csv.DictReader(io.StringIO(text)))
    assert rows == []


# ── Markdown ──────────────────────────────────────────────────────────────────


def test_markdown_contains_sections(sample_result: EnvDiffResult) -> None:
    text = export_result(sample_result, "markdown")
    assert "## Missing in second file" in text
    assert "## Missing in first file" in text
    assert "## Mismatched values" in text


def test_markdown_lists_keys(sample_result: EnvDiffResult) -> None:
    text = export_result(sample_result, "markdown")
    assert "ONLY_IN_FIRST" in text
    assert "ONLY_IN_SECOND" in text
    assert "SHARED_KEY" in text


def test_markdown_empty_sections(empty_result: EnvDiffResult) -> None:
    text = export_result(empty_result, "markdown")
    assert text.count("_None_") == 3


# ── Unsupported format ────────────────────────────────────────────────────────


def test_unsupported_format_raises(sample_result: EnvDiffResult) -> None:
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_result(sample_result, "xml")  # type: ignore[arg-type]
