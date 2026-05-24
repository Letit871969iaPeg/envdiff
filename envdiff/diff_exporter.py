"""Exports an EnvDiff to JSON, CSV, or Markdown."""
from __future__ import annotations

import csv
import io
import json
from typing import IO

from envdiff.differ import EnvDiff


def export_diff(diff: EnvDiff, fmt: str, stream: IO[str]) -> None:
    """Serialize *diff* in the requested format to *stream*."""
    fmt = fmt.lower()
    if fmt == "json":
        stream.write(_to_json(diff))
    elif fmt == "csv":
        stream.write(_to_csv(diff))
    elif fmt == "markdown":
        stream.write(_to_markdown(diff))
    else:
        raise ValueError(f"Unsupported format: {fmt!r}")


def _to_json(diff: EnvDiff) -> str:
    data = {
        "left": diff.left_path,
        "right": diff.right_path,
        "identical": diff.is_identical(),
        "lines": [
            {
                "kind": l.kind,
                "key": l.key,
                "left_value": l.left_value,
                "right_value": l.right_value,
            }
            for l in diff.lines
        ],
    }
    return json.dumps(data, indent=2)


def _to_csv(diff: EnvDiff) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["kind", "key", "left_value", "right_value"])
    for l in diff.lines:
        writer.writerow([l.kind, l.key, l.left_value or "", l.right_value or ""])
    return buf.getvalue()


def _to_markdown(diff: EnvDiff) -> str:
    lines = [
        f"## Diff: `{diff.left_path}` vs `{diff.right_path}`",
        "",
        "| Kind | Key | Left Value | Right Value |",
        "|------|-----|------------|-------------|" ,
    ]
    for l in diff.lines:
        lines.append(
            f"| {l.kind} | `{l.key}` | {l.left_value or ''} | {l.right_value or ''} |"
        )
    lines.append("")
    return "\n".join(lines)
