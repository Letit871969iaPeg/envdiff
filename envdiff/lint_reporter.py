"""Console reporter for lint results."""
from __future__ import annotations

from typing import List

from envdiff.linter import LintResult


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _severity_color(severity: str, text: str) -> str:
    if severity == "error":
        return _color(text, "31")
    return _color(text, "33")


def print_lint_report(result: LintResult, *, use_color: bool = True) -> None:
    """Print lint issues for a single file."""
    header = f"=== Lint: {result.path} ==="
    print(_color(header, "1") if use_color else header)

    if not result.has_issues():
        msg = "  No issues found."
        print(_color(msg, "32") if use_color else msg)
        return

    for issue in result.issues:
        tag = f"[{issue.severity.upper()}]"
        colored_tag = _severity_color(issue.severity, tag) if use_color else tag
        print(f"  {colored_tag} line {issue.line_number}: {issue.key!r} — {issue.message}")

    errors = len(result.errors())
    warnings = len(result.warnings())
    summary = f"  {errors} error(s), {warnings} warning(s)"
    print(_color(summary, "1") if use_color else summary)


def print_multi_lint_report(results: List[LintResult], *, use_color: bool = True) -> None:
    """Print lint reports for multiple files."""
    for result in results:
        print_lint_report(result, use_color=use_color)
        print()

    total_errors = sum(len(r.errors()) for r in results)
    total_warnings = sum(len(r.warnings()) for r in results)
    summary = f"Total: {total_errors} error(s), {total_warnings} warning(s) across {len(results)} file(s)"
    print(_color(summary, "1") if use_color else summary)
