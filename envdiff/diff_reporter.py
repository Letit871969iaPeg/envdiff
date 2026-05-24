"""Renders an EnvDiff to the terminal with colour coding."""
from __future__ import annotations

from envdiff.differ import EnvDiff
from envdiff.reporter import _color

_SYMBOLS = {
    "added": ("green", "+"),
    "removed": ("red", "-"),
    "changed": ("yellow", "~"),
    "unchanged": ("reset", " "),
}


def print_diff_report(diff: EnvDiff, show_unchanged: bool = False) -> None:
    """Print a coloured diff report to stdout."""
    print(_color("bold", f"--- {diff.left_path}"))
    print(_color("bold", f"+++ {diff.right_path}"))
    print()

    if diff.is_identical():
        print(_color("green", "Files are identical."))
        return

    for line in diff.lines:
        if line.kind == "unchanged" and not show_unchanged:
            continue
        color, symbol = _SYMBOLS[line.kind]
        if line.kind == "added":
            msg = f"{symbol} {line.key}={line.right_value}"
        elif line.kind == "removed":
            msg = f"{symbol} {line.key}={line.left_value}"
        elif line.kind == "changed":
            msg = f"{symbol} {line.key}: {line.left_value!r} -> {line.right_value!r}"
        else:
            msg = f"{symbol} {line.key}={line.left_value}"
        print(_color(color, msg))

    print()
    summary_parts = []
    if diff.added:
        summary_parts.append(_color("green", f"+{len(diff.added)} added"))
    if diff.removed:
        summary_parts.append(_color("red", f"-{len(diff.removed)} removed"))
    if diff.changed:
        summary_parts.append(_color("yellow", f"~{len(diff.changed)} changed"))
    print("Summary: " + ", ".join(summary_parts))
