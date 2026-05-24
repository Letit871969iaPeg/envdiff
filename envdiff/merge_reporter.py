"""Console reporter for merge results."""

from __future__ import annotations

from typing import List

from envdiff.merger import MergeResult
from envdiff.reporter import _color


def print_merge_report(result: MergeResult) -> None:
    """Print a human-readable merge summary to stdout."""
    total = len(result.all_keys)
    print(_color(f"Merged {len(result.all_files)} file(s) — {total} unique key(s) found.", "cyan"))
    print()

    universal: List[str] = []
    partial: List[str] = []

    for key in sorted(result.all_keys):
        missing = result.files_missing_key(key)
        if missing:
            partial.append(key)
        else:
            universal.append(key)

    if universal:
        print(_color(f"  Present in ALL files ({len(universal)}):", "green"))
        for key in universal:
            print(f"    {key}")
        print()

    if partial:
        print(_color(f"  Present in SOME files ({len(partial)}):", "yellow"))
        for key in partial:
            missing = result.files_missing_key(key)
            short = ", ".join(m.split("/")[-1] for m in missing)
            print(f"    {_color(key, 'yellow')}  (missing in: {short})")
        print()
