"""Sorts .env file keys alphabetically or by custom order and detects unsorted files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    """Result of a sort analysis on a single .env file."""

    path: str
    original_keys: List[str]
    sorted_keys: List[str]
    is_sorted: bool
    out_of_order: List[tuple] = field(default_factory=list)  # (index, key, expected_key)

    def render(self, comment: bool = True) -> str:
        """Render the sorted .env content as a string."""
        lines = []
        if comment:
            lines.append(f"# Sorted by envdiff — {self.path}")
        for key in self.sorted_keys:
            lines.append(key)
        return "\n".join(lines) + "\n"


def analyze_sort(env_keys: Dict[str, str], path: str = "") -> SortResult:
    """Analyse whether the keys of a parsed env dict are alphabetically sorted."""
    original = list(env_keys.keys())
    sorted_order = sorted(original, key=lambda k: k.lower())
    is_sorted = original == sorted_order

    out_of_order: List[tuple] = []
    if not is_sorted:
        for idx, (orig, expected) in enumerate(zip(original, sorted_order)):
            if orig != expected:
                out_of_order.append((idx, orig, expected))

    # Build KEY=VALUE lines in sorted order
    sorted_keys_lines = [
        f"{k}={env_keys[k]}" if env_keys[k] != "" else f"{k}="
        for k in sorted_order
    ]

    return SortResult(
        path=path,
        original_keys=original,
        sorted_keys=sorted_keys_lines,
        is_sorted=is_sorted,
        out_of_order=out_of_order,
    )


def sort_env_files(parsed_files: Dict[str, Dict[str, str]]) -> Dict[str, SortResult]:
    """Analyse sort order for multiple parsed env files.

    Args:
        parsed_files: mapping of file path -> {key: value}

    Returns:
        mapping of file path -> SortResult
    """
    return {path: analyze_sort(env, path) for path, env in parsed_files.items()}
