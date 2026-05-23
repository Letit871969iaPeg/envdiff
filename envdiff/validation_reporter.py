"""Formats and prints ValidationResult objects to stdout."""

from envdiff.validator import ValidationResult
from envdiff.reporter import _color

_SEVERITY_COLOR = {
    "error": "red",
    "warning": "yellow",
}


def print_validation_report(result: ValidationResult, use_color: bool = True) -> None:
    """Print a human-readable validation report for a single file."""
    status_label = "INVALID" if result.has_errors else ("WARNINGS" if result.has_warnings else "OK")
    status_color = "red" if result.has_errors else ("yellow" if result.has_warnings else "green")

    header = f"Validation: {result.path}  [{status_label}]"
    print(_color(header, status_color) if use_color else header)

    if not result.issues:
        msg = "  No issues found."
        print(_color(msg, "green") if use_color else msg)
        return

    for issue in result.issues:
        color = _SEVERITY_COLOR.get(issue.severity, "white")
        line = f"  {issue}"
        print(_color(line, color) if use_color else line)

    error_count = sum(1 for i in result.issues if i.severity == "error")
    warn_count = sum(1 for i in result.issues if i.severity == "warning")
    summary = f"  Summary: {error_count} error(s), {warn_count} warning(s)"
    print(_color(summary, status_color) if use_color else summary)


def print_multi_validation_report(
    results: list[ValidationResult], use_color: bool = True
) -> None:
    """Print validation reports for multiple files."""
    for idx, result in enumerate(results):
        if idx > 0:
            print()
        print_validation_report(result, use_color=use_color)
