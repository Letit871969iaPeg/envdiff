"""Core comparison logic for .env file diffing."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from envdiff.parser import parse_env_file


@dataclass
class EnvDiffResult:
    """Result of comparing two .env files."""

    base_file: str
    compare_file: str
    missing_in_compare: List[str] = field(default_factory=list)
    missing_in_base: List[str] = field(default_factory=list)
    value_mismatches: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.missing_in_compare
            or self.missing_in_base
            or self.value_mismatches
        )


def compare_env_files(
    base_path: str,
    compare_path: str,
    check_values: bool = False,
) -> EnvDiffResult:
    """Compare two .env files and return the diff result.

    Args:
        base_path: Path to the base .env file (e.g., .env.example).
        compare_path: Path to the file being compared (e.g., .env.production).
        check_values: If True, also report value mismatches.

    Returns:
        EnvDiffResult containing all detected differences.
    """
    base_vars = parse_env_file(base_path)
    compare_vars = parse_env_file(compare_path)

    base_keys: Set[str] = set(base_vars.keys())
    compare_keys: Set[str] = set(compare_vars.keys())

    result = EnvDiffResult(base_file=base_path, compare_file=compare_path)
    result.missing_in_compare = sorted(base_keys - compare_keys)
    result.missing_in_base = sorted(compare_keys - base_keys)

    if check_values:
        for key in base_keys & compare_keys:
            base_val = base_vars[key]
            compare_val = compare_vars[key]
            if base_val != compare_val:
                result.value_mismatches[key] = (base_val, compare_val)

    return result
