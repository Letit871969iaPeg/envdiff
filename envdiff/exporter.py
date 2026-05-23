"""Export diff results to various formats (JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envdiff.comparator import EnvDiffResult

ExportFormat = Literal["json", "csv", "markdown"]


def export_result(result: EnvDiffResult, fmt: ExportFormat) -> str:
    """Serialize an EnvDiffResult to the requested format string."""
    if fmt == "json":
        return _to_json(result)
    if fmt == "csv":
        return _to_csv(result)
    if fmt == "markdown":
        return _to_markdown(result)
    raise ValueError(f"Unsupported export format: {fmt!r}")


def _to_json(result: EnvDiffResult) -> str:
    payload = {
        "missing_in_second": list(result.missing_in_second),
        "missing_in_first": list(result.missing_in_first),
        "mismatched": [
            {"key": k, "first": v1, "second": v2}
            for k, (v1, v2) in result.mismatched.items()
        ],
    }
    return json.dumps(payload, indent=2)


def _to_csv(result: EnvDiffResult) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["issue", "key", "value_first", "value_second"])
    for key in sorted(result.missing_in_second):
        writer.writerow(["missing_in_second", key, "", ""])
    for key in sorted(result.missing_in_first):
        writer.writerow(["missing_in_first", key, "", ""])
    for key, (v1, v2) in sorted(result.mismatched.items()):
        writer.writerow(["mismatched", key, v1, v2])
    return buf.getvalue()


def _to_markdown(result: EnvDiffResult) -> str:
    lines: list[str] = ["# envdiff Report\n"]

    def _section(title: str, rows: list[list[str]], headers: list[str]) -> None:
        lines.append(f"## {title}\n")
        if not rows:
            lines.append("_None_\n")
            return
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    _section(
        "Missing in second file",
        [[k] for k in sorted(result.missing_in_second)],
        ["Key"],
    )
    _section(
        "Missing in first file",
        [[k] for k in sorted(result.missing_in_first)],
        ["Key"],
    )
    _section(
        "Mismatched values",
        [[k, v1, v2] for k, (v1, v2) in sorted(result.mismatched.items())],
        ["Key", "First", "Second"],
    )
    return "\n".join(lines)
