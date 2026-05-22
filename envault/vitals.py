"""Project vitals: track key health metrics for a project (key count, last modified, snapshot count, tag count)."""
from __future__ import annotations

import time
from typing import Any

from envault.storage import load_store, save_store
from envault.projects import get_all_env

_VITALS_KEY = "__vitals__"


def _vitals_map(store_path: str, password: str) -> dict:
    store = load_store(store_path, password)
    return store.get(_VITALS_KEY, {})


def record_vitals(store_path: str, password: str, project: str) -> dict[str, Any]:
    """Snapshot current vitals for *project* and persist them."""
    store = load_store(store_path, password)

    if project not in store:
        raise KeyError(f"Project '{project}' not found.")

    env = get_all_env(store_path, password, project)
    key_count = len(env)

    # Count snapshots stored for this project.
    snapshot_prefix = f"__snapshot__{project}__"
    snapshot_count = sum(1 for k in store if k.startswith(snapshot_prefix))

    # Count tags.
    tags_key = f"__tags__{project}"
    tag_count = len(store.get(tags_key, {}).get("tags", []))

    entry: dict[str, Any] = {
        "project": project,
        "key_count": key_count,
        "snapshot_count": snapshot_count,
        "tag_count": tag_count,
        "recorded_at": time.time(),
    }

    vitals = store.get(_VITALS_KEY, {})
    vitals[project] = entry
    store[_VITALS_KEY] = vitals
    save_store(store_path, password, store)
    return entry


def get_vitals(store_path: str, password: str, project: str) -> dict[str, Any] | None:
    """Return the last recorded vitals for *project*, or None."""
    vitals = _vitals_map(store_path, password)
    return vitals.get(project)


def delete_vitals(store_path: str, password: str, project: str) -> bool:
    """Remove stored vitals for *project*. Returns True if they existed."""
    store = load_store(store_path, password)
    vitals = store.get(_VITALS_KEY, {})
    if project not in vitals:
        return False
    del vitals[project]
    store[_VITALS_KEY] = vitals
    save_store(store_path, password, store)
    return True


def list_vitals(store_path: str, password: str) -> list[dict[str, Any]]:
    """Return all recorded vitals entries, sorted by project name."""
    vitals = _vitals_map(store_path, password)
    return sorted(vitals.values(), key=lambda e: e["project"])
