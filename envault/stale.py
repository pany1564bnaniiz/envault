"""Stale project detection — flag projects whose env keys haven't changed
within a configurable number of days."""

from __future__ import annotations

import time
from typing import Any

from envault.storage import load_store, save_store

_STALE_KEY = "__stale__"


def _stale_map(store: dict) -> dict:
    return store.setdefault(_STALE_KEY, {})


def touch_project(store_path: str, password: str, project: str) -> float:
    """Record the current time as the last-active timestamp for *project*.

    Returns the timestamp that was stored.
    """
    store = load_store(store_path, password)
    projects = {k for k in store if not k.startswith("__")}
    if project not in projects:
        raise KeyError(f"Project '{project}' does not exist.")
    ts = time.time()
    _stale_map(store)[project] = ts
    save_store(store_path, password, store)
    return ts


def get_last_active(store_path: str, password: str, project: str) -> float | None:
    """Return the last-active timestamp for *project*, or None if never touched."""
    store = load_store(store_path, password)
    return _stale_map(store).get(project)


def mark_stale(store_path: str, password: str, project: str) -> None:
    """Explicitly remove the last-active timestamp, marking the project stale."""
    store = load_store(store_path, password)
    sm = _stale_map(store)
    sm.pop(project, None)
    save_store(store_path, password, store)


def list_stale(
    store_path: str, password: str, days: int = 30
) -> list[dict[str, Any]]:
    """Return projects that have been inactive for more than *days* days.

    Projects that have never been touched are always considered stale.
    """
    store = load_store(store_path, password)
    sm = _stale_map(store)
    threshold = time.time() - days * 86400
    result = []
    for project in sorted(k for k in store if not k.startswith("__")):
        last = sm.get(project)
        if last is None or last < threshold:
            result.append({"project": project, "last_active": last})
    return result
