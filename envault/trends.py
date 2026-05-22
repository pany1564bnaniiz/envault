"""Track and analyse key-count trends for projects over time."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from envault.storage import load_store, save_store

_TRENDS_KEY = "__trends__"


def _trends_map(store_path: str, password: str) -> dict[str, Any]:
    store = load_store(store_path, password)
    return store.get(_TRENDS_KEY, {})


def record_snapshot(
    store_path: str,
    password: str,
    project: str,
) -> dict[str, Any]:
    """Record a trend snapshot (key count) for *project* at the current time."""
    store = load_store(store_path, password)

    if project not in store or project == _TRENDS_KEY:
        raise KeyError(f"Project '{project}' not found.")

    key_count = len(
        {
            k: v
            for k, v in store[project].items()
            if not k.startswith("__")
        }
    )

    entry: dict[str, Any] = {
        "project": project,
        "key_count": key_count,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }

    trends = store.setdefault(_TRENDS_KEY, {})
    trends.setdefault(project, []).append(entry)

    save_store(store_path, password, store)
    return entry


def get_trend(
    store_path: str,
    password: str,
    project: str,
) -> list[dict[str, Any]]:
    """Return all recorded snapshots for *project*, oldest first."""
    return list(_trends_map(store_path, password).get(project, []))


def clear_trend(
    store_path: str,
    password: str,
    project: str,
) -> int:
    """Delete all trend snapshots for *project*.  Returns the number removed."""
    store = load_store(store_path, password)
    trends: dict = store.get(_TRENDS_KEY, {})
    removed = len(trends.pop(project, []))
    if _TRENDS_KEY in store:
        store[_TRENDS_KEY] = trends
    save_store(store_path, password, store)
    return removed


def summarise_trend(
    store_path: str,
    password: str,
    project: str,
) -> dict[str, Any]:
    """Return a lightweight summary (first, latest, delta) for *project*."""
    snapshots = get_trend(store_path, password, project)
    if not snapshots:
        return {"project": project, "snapshots": 0}
    first = snapshots[0]["key_count"]
    latest = snapshots[-1]["key_count"]
    return {
        "project": project,
        "snapshots": len(snapshots),
        "first_count": first,
        "latest_count": latest,
        "delta": latest - first,
    }
