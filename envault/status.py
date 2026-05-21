"""Project status tracking for envault."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envault.storage import load_store, save_store

_VALID_STATUSES = {"active", "inactive", "deprecated", "experimental", "stable"}
_STATUS_KEY = "__status__"


def _status_map(store: dict) -> dict:
    return store.setdefault(_STATUS_KEY, {})


def set_status(
    store_path: str,
    password: str,
    project: str,
    status: str,
    note: Optional[str] = None,
) -> dict:
    """Set the status of a project."""
    if status not in _VALID_STATUSES:
        raise ValueError(
            f"Invalid status {status!r}. Must be one of: {sorted(_VALID_STATUSES)}"
        )
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project {project!r} not found.")
    entry = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "note": note,
    }
    _status_map(store)[project] = entry
    save_store(store_path, password, store)
    return entry


def get_status(store_path: str, password: str, project: str) -> Optional[dict]:
    """Return the status entry for a project, or None if unset."""
    store = load_store(store_path, password)
    return _status_map(store).get(project)


def remove_status(store_path: str, password: str, project: str) -> bool:
    """Remove the status for a project. Returns True if removed."""
    store = load_store(store_path, password)
    mapping = _status_map(store)
    if project not in mapping:
        return False
    del mapping[project]
    save_store(store_path, password, store)
    return True


def list_statuses(store_path: str, password: str) -> dict[str, dict]:
    """Return a mapping of project -> status entry for all projects with a status."""
    store = load_store(store_path, password)
    return dict(_status_map(store))


def projects_by_status(store_path: str, password: str, status: str) -> list[str]:
    """Return project names that have the given status."""
    return [
        proj
        for proj, entry in list_statuses(store_path, password).items()
        if entry.get("status") == status
    ]
