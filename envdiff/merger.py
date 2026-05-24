"""Merge multiple .env files into a unified template with all known keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from envdiff.parser import parse_env_file


@dataclass
class MergeResult:
    """Result of merging multiple .env files."""

    keys: Dict[str, str] = field(default_factory=dict)
    """Merged keys with their resolved values (last-write-wins by default)."""

    sources: Dict[str, List[str]] = field(default_factory=dict)
    """Maps each key to the list of files that defined it."""

    all_files: List[str] = field(default_factory=list)
    """Ordered list of source file paths."""

    @property
    def all_keys(self) -> Set[str]:
        return set(self.keys.keys())

    def files_missing_key(self, key: str) -> List[str]:
        """Return files that do NOT define the given key."""
        defining = set(self.sources.get(key, []))
        return [f for f in self.all_files if f not in defining]


def merge_env_files(
    paths: List[str],
    strategy: str = "last",
) -> MergeResult:
    """Merge .env files into a single MergeResult.

    Args:
        paths: Ordered list of .env file paths.
        strategy: ``'last'`` keeps the last value seen; ``'first'`` keeps the
                  first value seen for each key.

    Returns:
        A :class:`MergeResult` containing merged keys and provenance data.
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}. Use 'first' or 'last'.")

    result = MergeResult(all_files=list(paths))

    for path in paths:
        env = parse_env_file(path)
        for key, value in env.items():
            if strategy == "first" and key in result.keys:
                pass  # keep existing
            else:
                result.keys[key] = value
            result.sources.setdefault(key, [])
            if path not in result.sources[key]:
                result.sources[key].append(path)

    return result


def render_merged_template(
    result: MergeResult,
    placeholder: Optional[str] = "",
) -> str:
    """Render a merged .env template string from a MergeResult.

    Keys present in all source files retain their resolved value; keys missing
    from some files are annotated with a comment listing the absent files.

    Args:
        result: A :class:`MergeResult` from :func:`merge_env_files`.
        placeholder: Value to use for keys with an empty resolved value.

    Returns:
        A string suitable for writing to a ``.env`` file.
    """
    lines: List[str] = []
    for key in sorted(result.all_keys):
        missing = result.files_missing_key(key)
        if missing:
            short = [m.split("/")[-1] for m in missing]
            lines.append(f"# WARNING: missing in {', '.join(short)}")
        value = result.keys[key] if result.keys[key] != "" else placeholder
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"
