"""Scanner: detect .env files in a directory tree."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


_DEFAULT_PATTERNS = (".env", ".env.*", "*.env")


@dataclass
class ScanResult:
    root: Path
    found: List[Path] = field(default_factory=list)
    skipped: List[Path] = field(default_factory=list)

    @property
    def total_found(self) -> int:
        return len(self.found)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped)


def _matches_patterns(name: str, patterns: tuple[str, ...]) -> bool:
    from fnmatch import fnmatch
    return any(fnmatch(name, pat) for pat in patterns)


def scan_for_env_files(
    root: str | Path,
    patterns: Optional[tuple[str, ...]] = None,
    max_depth: int = 5,
    skip_hidden_dirs: bool = True,
) -> ScanResult:
    """Walk *root* up to *max_depth* levels and collect env-like files."""
    root = Path(root).resolve()
    if patterns is None:
        patterns = _DEFAULT_PATTERNS

    result = ScanResult(root=root)

    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        depth = len(current.relative_to(root).parts)

        if depth >= max_depth:
            dirnames.clear()
            continue

        if skip_hidden_dirs:
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".")
                and d not in ("node_modules", "__pycache__", ".git", ".venv", "venv")
            ]

        for filename in filenames:
            filepath = current / filename
            if _matches_patterns(filename, patterns):
                try:
                    filepath.read_text(encoding="utf-8")
                    result.found.append(filepath)
                except (PermissionError, OSError):
                    result.skipped.append(filepath)

    result.found.sort()
    result.skipped.sort()
    return result
