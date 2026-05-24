"""Group .env keys by prefix and report on structural organization."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class GroupResult:
    """Result of grouping env keys by prefix."""
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)
    separator: str = "_"

    @property
    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    @property
    def total_keys(self) -> int:
        return sum(len(v) for v in self.groups.values()) + len(self.ungrouped)

    def largest_group(self) -> Tuple[str, int]:
        if not self.groups:
            return ("", 0)
        name = max(self.groups, key=lambda k: len(self.groups[k]))
        return (name, len(self.groups[name]))


def group_env_keys(
    env: Dict[str, str],
    separator: str = "_",
    min_group_size: int = 1,
) -> GroupResult:
    """Group keys by their first prefix segment.

    Keys without a separator (or whose prefix group has fewer than
    ``min_group_size`` members) are placed in ``ungrouped``.
    """
    prefix_map: Dict[str, List[str]] = defaultdict(list)

    for key in env:
        if separator in key:
            prefix = key.split(separator, 1)[0]
            prefix_map[prefix].append(key)
        else:
            prefix_map[""].append(key)

    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = list(prefix_map.pop("", []))

    for prefix, keys in prefix_map.items():
        if len(keys) >= min_group_size:
            groups[prefix] = sorted(keys)
        else:
            ungrouped.extend(keys)

    return GroupResult(groups=groups, ungrouped=sorted(ungrouped), separator=separator)


def group_env_files(
    envs: Dict[str, Dict[str, str]],
    separator: str = "_",
    min_group_size: int = 1,
) -> Dict[str, GroupResult]:
    """Apply :func:`group_env_keys` to multiple named env dicts."""
    return {
        name: group_env_keys(env, separator=separator, min_group_size=min_group_size)
        for name, env in envs.items()
    }
