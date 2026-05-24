"""Redacts sensitive values in .env files based on key patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Patterns that suggest a value is sensitive
SENSITIVE_PATTERNS: List[re.Pattern] = [
    re.compile(r"(password|passwd|pwd)", re.IGNORECASE),
    re.compile(r"(secret|token|api[_-]?key|apikey)", re.IGNORECASE),
    re.compile(r"(private[_-]?key|priv[_-]?key)", re.IGNORECASE),
    re.compile(r"(auth|credential|cred)", re.IGNORECASE),
    re.compile(r"(dsn|database[_-]?url|db[_-]?url)", re.IGNORECASE),
]

REDACT_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def redact_count(self) -> int:
        return len(self.redacted_keys)


def is_sensitive_key(key: str) -> bool:
    """Return True if the key name matches any sensitive pattern."""
    return any(pattern.search(key) for pattern in SENSITIVE_PATTERNS)


def redact_env(
    env: Dict[str, str],
    extra_patterns: List[str] | None = None,
) -> RedactResult:
    """Redact sensitive values from an env dict.

    Args:
        env: Parsed environment dict.
        extra_patterns: Additional regex patterns (as strings) to treat as sensitive.

    Returns:
        A RedactResult with the redacted dict and list of redacted keys.
    """
    compiled_extras: List[re.Pattern] = []
    if extra_patterns:
        for p in extra_patterns:
            try:
                compiled_extras.append(re.compile(p, re.IGNORECASE))
            except re.error:
                pass

    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        all_patterns = SENSITIVE_PATTERNS + compiled_extras
        if any(pat.search(key) for pat in all_patterns):
            redacted[key] = REDACT_PLACEHOLDER
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(original=env, redacted=redacted, redacted_keys=sorted(redacted_keys))
