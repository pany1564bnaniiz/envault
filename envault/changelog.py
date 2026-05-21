"""Per-project changelog: record and retrieve human-readable change summaries."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envault.storage import load_store, save_store

_CHANGELOG_KEY = "__changelog__"


def _changelog_map(store: dict) -> dict:
    return store.setdefault(_CHANGELOG_KEY, {})


def add_entry(
    store_path,
    password: str,
    project: str,
    message: str,
    author: str = "envault",
) -> dict:
    """Append a changelog entry for *project* and persist the store."""
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' does not exist.")
    changelog = _changelog_map(store)
    entries = changelog.setdefault(project, [])
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "author": author,
        "message": message,
    }
    entries.append(entry)
    save_store(store_path, password, store)
    return entry


def get_changelog(store_path, password: str, project: str) -> list[dict]:
    """Return all changelog entries for *project* (oldest first)."""
    store = load_store(store_path, password)
    return list(_changelog_map(store).get(project, []))


def clear_changelog(store_path, password: str, project: str) -> int:
    """Remove all changelog entries for *project*. Returns number removed."""
    store = load_store(store_path, password)
    changelog = _changelog_map(store)
    removed = len(changelog.pop(project, []))
    save_store(store_path, password, store)
    return removed
