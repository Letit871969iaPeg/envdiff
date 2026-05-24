"""Lint .env files for style and convention issues."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class LintIssue:
    line_number: int
    key: str
    message: str
    severity: str  # 'warning' | 'error'

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] line {self.line_number}: {self.key!r} — {self.message}"


@dataclass
class LintResult:
    path: str
    issues: List[LintIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(self.issues)

    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


_UPPER_SNAKE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_LOWER_KEY = re.compile(r'^[a-z]')
_WHITESPACE_AROUND_EQ = re.compile(r'\s=|=\s')


def lint_env_file(path: str) -> LintResult:
    """Lint a single .env file and return a LintResult."""
    result = LintResult(path=path)
    try:
        lines = Path(path).read_text().splitlines()
    except FileNotFoundError:
        result.issues.append(LintIssue(0, "", f"File not found: {path}", "error"))
        return result

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if "=" not in stripped:
            result.issues.append(LintIssue(lineno, stripped, "Missing '=' separator", "error"))
            continue

        key, _, value = stripped.partition("=")

        if _WHITESPACE_AROUND_EQ.search(raw):
            result.issues.append(LintIssue(lineno, key, "Whitespace around '=' is not portable", "warning"))

        if not _UPPER_SNAKE.match(key):
            if _LOWER_KEY.match(key):
                result.issues.append(LintIssue(lineno, key, "Key should use UPPER_SNAKE_CASE", "warning"))
            else:
                result.issues.append(LintIssue(lineno, key, "Key contains invalid characters", "error"))

        if value.startswith(' ') or value.endswith(' '):
            result.issues.append(LintIssue(lineno, key, "Value has leading/trailing whitespace", "warning"))

        if len(raw) > 200:
            result.issues.append(LintIssue(lineno, key, "Line exceeds 200 characters", "warning"))

    return result


def lint_env_files(paths: List[str]) -> List[LintResult]:
    """Lint multiple .env files."""
    return [lint_env_file(p) for p in paths]
