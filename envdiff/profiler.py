"""Profile .env files: count keys, detect duplicates, measure value lengths."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.parser import parse_env_file


@dataclass
class ProfileResult:
    path: str
    total_keys: int
    duplicate_keys: List[str]
    empty_values: List[str]
    longest_key: Tuple[str, int]       # (key, length)
    longest_value: Tuple[str, int]     # (key, value_length)
    avg_value_length: float
    key_lengths: Dict[str, int] = field(default_factory=dict)

    @property
    def has_duplicates(self) -> bool:
        return len(self.duplicate_keys) > 0

    @property
    def has_empty_values(self) -> bool:
        return len(self.empty_values) > 0


def profile_env_file(path: str) -> ProfileResult:
    """Analyse a single .env file and return a ProfileResult."""
    # Re-read raw lines to catch duplicates (parser deduplicates via dict)
    duplicate_keys: List[str] = []
    seen: Dict[str, int] = {}

    try:
        with open(path, encoding="utf-8") as fh:
            raw_lines = fh.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")

    for raw in raw_lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key = line.split("=", 1)[0].strip()
            seen[key] = seen.get(key, 0) + 1

    duplicate_keys = [k for k, count in seen.items() if count > 1]

    env = parse_env_file(path)

    empty_values = [k for k, v in env.items() if v == ""]

    if env:
        lk = max(env.keys(), key=len)
        lv_key = max(env.keys(), key=lambda k: len(env[k]))
        avg = sum(len(v) for v in env.values()) / len(env)
    else:
        lk = ("", 0)
        lv_key = ""
        avg = 0.0
        return ProfileResult(
            path=path,
            total_keys=0,
            duplicate_keys=duplicate_keys,
            empty_values=[],
            longest_key=("", 0),
            longest_value=("", 0),
            avg_value_length=0.0,
        )

    return ProfileResult(
        path=path,
        total_keys=len(env),
        duplicate_keys=duplicate_keys,
        empty_values=empty_values,
        longest_key=(lk, len(lk)),
        longest_value=(lv_key, len(env[lv_key])),
        avg_value_length=round(avg, 2),
        key_lengths={k: len(k) for k in env},
    )
