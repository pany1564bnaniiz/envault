"""Sprint tracking for envault projects."""
from __future__ import annotations

from datetime import date
from typing import Optional

from envault.storage import load_store, save_store

_SPRINTS_KEY = "__sprints__"


def _sprints_map(store: dict) -> dict:
    return store.setdefault(_SPRINTS_KEY, {})


def set_sprint(
    store_path,
    password: str,
    project: str,
    sprint_name: str,
    start_date: str,
    end_date: str,
    description: str = "",
) -> dict:
    """Assign a sprint to a project."""
    store = load_store(store_path, password)
    if project not in store and project != _SPRINTS_KEY:
        raise KeyError(f"Project '{project}' does not exist.")
    # validate date format
    for ds, label in ((start_date, "start_date"), (end_date, "end_date")):
        try:
            date.fromisoformat(ds)
        except ValueError:
            raise ValueError(f"Invalid ISO date for {label}: '{ds}'")
    if end_date < start_date:
        raise ValueError("end_date must not be before start_date.")
    entry = {
        "sprint": sprint_name,
        "start": start_date,
        "end": end_date,
        "description": description,
    }
    _sprints_map(store)[project] = entry
    save_store(store_path, password, store)
    return entry


def get_sprint(store_path, password: str, project: str) -> Optional[dict]:
    """Return the sprint entry for *project*, or None."""
    store = load_store(store_path, password)
    return _sprints_map(store).get(project)


def delete_sprint(store_path, password: str, project: str) -> bool:
    """Remove the sprint for *project*. Returns True if it existed."""
    store = load_store(store_path, password)
    sprints = _sprints_map(store)
    if project not in sprints:
        return False
    del sprints[project]
    save_store(store_path, password, store)
    return True


def list_sprints(store_path, password: str) -> dict:
    """Return mapping of project -> sprint entry for all assigned sprints."""
    store = load_store(store_path, password)
    return dict(_sprints_map(store))


def active_sprints(store_path, password: str, as_of: Optional[str] = None) -> dict:
    """Return sprints whose date range includes *as_of* (defaults to today)."""
    today = as_of or date.today().isoformat()
    return {
        proj: entry
        for proj, entry in list_sprints(store_path, password).items()
        if entry["start"] <= today <= entry["end"]
    }
