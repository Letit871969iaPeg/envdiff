"""Prints a human-readable report of redaction results."""

from __future__ import annotations

from envdiff.redactor import RedactResult


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def print_redact_report(result: RedactResult, filename: str = "") -> None:
    """Print a summary of which keys were redacted."""
    label = f" ({filename})" if filename else ""
    print(_color(f"Redaction Report{label}", "1;36"))
    print(_color("-" * 40, "36"))

    if result.redact_count == 0:
        print(_color("  No sensitive keys detected.", "32"))
    else:
        print(
            _color(
                f"  {result.redact_count} key(s) redacted:",
                "33",
            )
        )
        for key in result.redacted_keys:
            print(f"    {_color(key, '31')} → {_color('***REDACTED***', '90')}")

    total = len(result.original)
    safe = total - result.redact_count
    print()
    print(f"  Total keys : {total}")
    print(f"  Safe       : {_color(str(safe), '32')}")
    print(f"  Redacted   : {_color(str(result.redact_count), '33')}")
    print()
