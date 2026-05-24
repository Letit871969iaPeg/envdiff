"""Console reporter for ProfileResult."""
from __future__ import annotations

from typing import List

from envdiff.profiler import ProfileResult


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def print_profile_report(result: ProfileResult) -> None:
    """Print a human-readable profile summary for one file."""
    print(_color(f"\n=== Profile: {result.path} ===", "1;36"))
    print(f"  Total keys       : {result.total_keys}")
    print(f"  Avg value length : {result.avg_value_length}")

    if result.longest_key[0]:
        print(f"  Longest key      : {result.longest_key[0]!r} ({result.longest_key[1]} chars)")
        print(f"  Longest value    : key={result.longest_value[0]!r} ({result.longest_value[1]} chars)")

    if result.has_duplicates:
        label = _color("DUPLICATES", "1;31")
        print(f"  {label}        : {', '.join(result.duplicate_keys)}")
    else:
        print(f"  Duplicates       : " + _color("none", "32"))

    if result.has_empty_values:
        label = _color("EMPTY VALUES", "1;33")
        keys = ", ".join(result.empty_values)
        print(f"  {label}     : {keys}")
    else:
        print(f"  Empty values     : " + _color("none", "32"))


def print_multi_profile_report(results: List[ProfileResult]) -> None:
    """Print profile reports for multiple files."""
    for r in results:
        print_profile_report(r)
    print()
