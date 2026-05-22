"""Objectives: attach goal/objective text to projects."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envault.storage import load_store, save_store

_OBJECTIVES_KEY = "__objectives__"


def _objectives_map(store_path, password):
    store = load_store(store_path, password)
    return store.get(_OBJECTIVES_KEY, {})


def set_objective(
    store_path,
    password: str,
    project: str,
    text: str,
    due: Optional[str] = None,
) -> dict:
    """Set or replace the objective for *project*."""
    store = load_store(store_path, password)
    if project not in store and project != _OBJECTIVES_KEY:
        raise KeyError(f"Project '{project}' does not exist.")
    objectives = store.setdefault(_OBJECTIVES_KEY, {})
    entry = {
        "text": text,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if due is not None:
        entry["due"] = due
    objectives[project] = entry
    save_store(store_path, password, store)
    return entry


def get_objective(store_path, password: str, project: str) -> Optional[dict]:
    """Return the objective entry for *project*, or None."""
    objectives = _objectives_map(store_path, password)
    return objectives.get(project)


def delete_objective(store_path, password: str, project: str) -> bool:
    """Delete the objective for *project*. Returns True if it existed."""
    store = load_store(store_path, password)
    objectives = store.get(_OBJECTIVES_KEY, {})
    if project not in objectives:
        return False
    del objectives[project]
    store[_OBJECTIVES_KEY] = objectives
    save_store(store_path, password, store)
    return True


def list_objectives(store_path, password: str) -> dict:
    """Return all project -> objective entry mappings."""
    return dict(_objectives_map(store_path, password))
