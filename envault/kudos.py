"""Kudos — let users give positive recognition to projects."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from envault.storage import load_store, save_store

_KUDOS_KEY = "__kudos__"


def _kudos_map(store_path: str, password: str) -> dict[str, Any]:
    store = load_store(store_path, password)
    return store.get(_KUDOS_KEY, {})


def give_kudos(
    store_path: str,
    password: str,
    project: str,
    actor: str,
    message: str = "",
) -> dict[str, Any]:
    """Record a kudos entry for *project* from *actor*."""
    store = load_store(store_path, password)
    # Ensure the project exists
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    kudos_map = store.setdefault(_KUDOS_KEY, {})
    entries: list[dict[str, Any]] = kudos_map.setdefault(project, [])
    entry: dict[str, Any] = {
        "actor": actor,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    entries.append(entry)
    save_store(store_path, password, store)
    return entry


def get_kudos(store_path: str, password: str, project: str) -> list[dict[str, Any]]:
    """Return all kudos entries for *project*."""
    return _kudos_map(store_path, password).get(project, [])


def kudos_count(store_path: str, password: str, project: str) -> int:
    """Return the total number of kudos for *project*."""
    return len(get_kudos(store_path, password, project))


def clear_kudos(store_path: str, password: str, project: str) -> int:
    """Remove all kudos for *project*. Returns the number of entries removed."""
    store = load_store(store_path, password)
    kudos_map: dict[str, Any] = store.get(_KUDOS_KEY, {})
    removed = len(kudos_map.pop(project, []))
    store[_KUDOS_KEY] = kudos_map
    save_store(store_path, password, store)
    return removed
