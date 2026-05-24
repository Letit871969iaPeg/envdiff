"""Generates a unified diff-style view between two .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.parser import parse_env_file


@dataclass
class DiffLine:
    """Represents a single line in the diff output."""
    kind: str  # 'added', 'removed', 'changed', 'unchanged'
    key: str
    left_value: str | None = None
    right_value: str | None = None

    def __str__(self) -> str:
        if self.kind == "added":
            return f"+ {self.key}={self.right_value}"
        if self.kind == "removed":
            return f"- {self.key}={self.left_value}"
        if self.kind == "changed":
            return f"~ {self.key}: {self.left_value!r} -> {self.right_value!r}"
        return f"  {self.key}={self.left_value}"


@dataclass
class EnvDiff:
    """Full diff result between two .env files."""
    left_path: str
    right_path: str
    lines: List[DiffLine] = field(default_factory=list)

    @property
    def added(self) -> List[DiffLine]:
        return [l for l in self.lines if l.kind == "added"]

    @property
    def removed(self) -> List[DiffLine]:
        return [l for l in self.lines if l.kind == "removed"]

    @property
    def changed(self) -> List[DiffLine]:
        return [l for l in self.lines if l.kind == "changed"]

    @property
    def unchanged(self) -> List[DiffLine]:
        return [l for l in self.lines if l.kind == "unchanged"]

    def is_identical(self) -> bool:
        return len(self.added) == 0 and len(self.removed) == 0 and len(self.changed) == 0


def diff_env_files(left_path: str, right_path: str) -> EnvDiff:
    """Compare two .env files and return a structured diff."""
    left: Dict[str, str] = parse_env_file(left_path)
    right: Dict[str, str] = parse_env_file(right_path)

    all_keys = sorted(set(left) | set(right))
    lines: List[DiffLine] = []

    for key in all_keys:
        in_left = key in left
        in_right = key in right
        if in_left and in_right:
            if left[key] == right[key]:
                lines.append(DiffLine("unchanged", key, left[key], right[key]))
            else:
                lines.append(DiffLine("changed", key, left[key], right[key]))
        elif in_left:
            lines.append(DiffLine("removed", key, left[key], None))
        else:
            lines.append(DiffLine("added", key, None, right[key]))

    return EnvDiff(left_path=left_path, right_path=right_path, lines=lines)
