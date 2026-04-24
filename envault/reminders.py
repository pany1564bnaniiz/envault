"""Reminders: schedule a reminder message for a project at a future date."""
from __future__ import annotations

import time
from typing import Optional

from envault.storage import load_store, save_store

_REMINDERS_KEY = "__reminders__"


def _reminders_map(store: dict) -> dict:
    return store.setdefault(_REMINDERS_KEY, {})


def set_reminder(
    store_path: str,
    password: str,
    project: str,
    message: str,
    due_ts: float,
) -> None:
    """Set (or overwrite) a reminder for *project*."""
    store = load_store(store_path, password)
    if project not in store and project != _REMINDERS_KEY:
        raise KeyError(f"Project '{project}' not found.")
    _reminders_map(store)[project] = {"message": message, "due": due_ts}
    save_store(store_path, password, store)


def get_reminder(
    store_path: str, password: str, project: str
) -> Optional[dict]:
    """Return the reminder dict for *project*, or None if unset."""
    store = load_store(store_path, password)
    return _reminders_map(store).get(project)


def delete_reminder(store_path: str, password: str, project: str) -> None:
    """Remove the reminder for *project*. Silently ignores missing entries."""
    store = load_store(store_path, password)
    rm = _reminders_map(store)
    if project in rm:
        del rm[project]
        save_store(store_path, password, store)


def due_reminders(store_path: str, password: str) -> list[dict]:
    """Return all reminders whose due timestamp is <= now, sorted by due date."""
    store = load_store(store_path, password)
    now = time.time()
    results = [
        {"project": proj, **info}
        for proj, info in _reminders_map(store).items()
        if info["due"] <= now
    ]
    return sorted(results, key=lambda r: r["due"])


def list_reminders(store_path: str, password: str) -> list[dict]:
    """Return all reminders sorted by due date."""
    store = load_store(store_path, password)
    results = [
        {"project": proj, **info}
        for proj, info in _reminders_map(store).items()
    ]
    return sorted(results, key=lambda r: r["due"])
