"""Validates .env files for common issues like duplicate keys, invalid syntax, and empty values."""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ValidationIssue:
    line_number: int
    key: str
    message: str
    severity: str  # 'error' | 'warning'

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] Line {self.line_number}: {self.key!r} — {self.message}"


@dataclass
class ValidationResult:
    path: str
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    @property
    def is_valid(self) -> bool:
        return not self.has_errors


def validate_env_file(path: str) -> ValidationResult:
    """Read a .env file and return a ValidationResult with any issues found."""
    result = ValidationResult(path=path)
    seen_keys: Dict[str, int] = {}

    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except FileNotFoundError:
        result.issues.append(
            ValidationIssue(line_number=0, key="", message="File not found", severity="error")
        )
        return result

    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(
                ValidationIssue(lineno, line, "Missing '=' separator", "error")
            )
            continue

        key, _, value = line.partition("=")
        key = key.strip()

        if not key:
            result.issues.append(
                ValidationIssue(lineno, "", "Empty key", "error")
            )
            continue

        if key in seen_keys:
            result.issues.append(
                ValidationIssue(
                    lineno, key,
                    f"Duplicate key (first seen on line {seen_keys[key]})",
                    "warning",
                )
            )
        else:
            seen_keys[key] = lineno

        value = value.strip()
        if value == "":
            result.issues.append(
                ValidationIssue(lineno, key, "Empty value", "warning")
            )

    return result
