"""Milestone tracking for projects — attach named milestones with due dates."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from envault.storage import load_store, save_store

_MILESTONES_KEY = "__milestones__"


def _milestones_map(store: dict) -> dict:
    return store.setdefault(_MILESTONES_KEY, {})


def set_milestone(
    store_path: str,
    password: str,
    project: str,
    name: str,
    due: str,
    description: str = "",
) -> dict:
    """Create or update a milestone for *project*.

    *due* must be an ISO-8601 date string (YYYY-MM-DD or full datetime).
    Returns the stored milestone entry.
    """
    # Validate date
    try:
        datetime.fromisoformat(due)
    except ValueError:
        raise ValueError(f"Invalid ISO date: {due!r}")

    store = load_store(store_path, password)
    projects = {k for k in store if not k.startswith("__")}
    if project not in projects:
        raise KeyError(f"Project {project!r} not found")

    entry = {"name": name, "due": due, "description": description}
    _milestones_map(store).setdefault(project, {})[name] = entry
    save_store(store_path, password, store)
    return entry


def get_milestone(store_path: str, password: str, project: str, name: str) -> Optional[dict]:
    """Return the milestone dict or *None* if not found."""
    store = load_store(store_path, password)
    return _milestones_map(store).get(project, {}).get(name)


def delete_milestone(store_path: str, password: str, project: str, name: str) -> bool:
    """Remove a milestone. Returns True if it existed."""
    store = load_store(store_path, password)
    project_milestones = _milestones_map(store).get(project, {})
    if name not in project_milestones:
        return False
    del project_milestones[name]
    save_store(store_path, password, store)
    return True


def list_milestones(store_path: str, password: str, project: str) -> list[dict]:
    """Return all milestones for *project*, sorted by due date."""
    store = load_store(store_path, password)
    entries = _milestones_map(store).get(project, {}).values()
    return sorted(entries, key=lambda e: e["due"])


def overdue_milestones(
    store_path: str, password: str, project: str, as_of: Optional[str] = None
) -> list[dict]:
    """Return milestones whose due date is before *as_of* (defaults to now)."""
    cutoff = datetime.fromisoformat(as_of) if as_of else datetime.utcnow()
    return [
        m
        for m in list_milestones(store_path, password, project)
        if datetime.fromisoformat(m["due"]) < cutoff
    ]
