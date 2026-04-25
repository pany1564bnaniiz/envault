"""Diff utilities for comparing .env snapshots across versions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


def diff_envs(
    old: Dict[str, str],
    new: Dict[str, str],
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare two env dicts and return a list of DiffEntry records."""
    entries: List[DiffEntry] = []

    all_keys = set(old) | set(new)

    for key in sorted(all_keys):
        if key in old and key not in new:
            entries.append(DiffEntry(key=key, status="removed", old_value=old[key]))
        elif key not in old and key in new:
            entries.append(DiffEntry(key=key, status="added", new_value=new[key]))
        elif old[key] != new[key]:
            entries.append(
                DiffEntry(key=key, status="changed", old_value=old[key], new_value=new[key])
            )
        else:
            if show_unchanged:
                entries.append(
                    DiffEntry(key=key, status="unchanged", old_value=old[key], new_value=new[key])
                )

    return entries


def diff_summary(entries: List[DiffEntry]) -> Dict[str, int]:
    """Return a count of each status type in the diff entries.

    Example::

        >>> summary = diff_summary(entries)
        >>> print(summary)
        {'added': 2, 'removed': 0, 'changed': 1, 'unchanged': 5}
    """
    summary: Dict[str, int] = {"added": 0, "removed": 0, "changed": 0, "unchanged": 0}
    for entry in entries:
        if entry.status in summary:
            summary[entry.status] += 1
    return summary


def format_diff(entries: List[DiffEntry], mask_values: bool = True) -> str:
    """Render diff entries as a human-readable string."""
    if not entries:
        return "No differences found."

    lines: List[str] = []
    for e in entries:
        if e.status == "added":
            val = "***" if mask_values else e.new_value
            lines.append(f"  + {e.key}={val}")
        elif e.status == "removed":
            val = "***" if mask_values else e.old_value
            lines.append(f"  - {e.key}={val}")
        elif e.status == "changed":
            if mask_values:
                lines.append(f"  ~ {e.key}: *** -> ***")
            else:
                lines.append(f"  ~ {e.key}: {e.old_value!r} -> {e.new_value!r}")
        else:
            val = "***" if mask_values else e.old_value
            lines.append(f"    {e.key}={val}")
    return "\n".join(lines)
