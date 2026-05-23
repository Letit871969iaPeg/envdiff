"""Parser for .env files."""

import re
from pathlib import Path
from typing import Dict, Optional


ENV_LINE_PATTERN = re.compile(
    r"^\s*(?!#)(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$"
)


def parse_env_file(filepath: str | Path) -> Dict[str, Optional[str]]:
    """Parse a .env file and return a dict of key-value pairs.

    Args:
        filepath: Path to the .env file.

    Returns:
        Dictionary mapping variable names to their values.
        Values are stripped of surrounding quotes.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {filepath}")

    env_vars: Dict[str, Optional[str]] = {}

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = ENV_LINE_PATTERN.match(line)
            if match:
                key = match.group("key")
                value = match.group("value").strip()
                value = _strip_quotes(value)
                env_vars[key] = value if value != "" else None

    return env_vars


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
    return value
