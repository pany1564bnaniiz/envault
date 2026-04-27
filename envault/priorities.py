"""Project priority management for envault."""

from __future__ import annotations

from typing import Dict, List, Optional

from envault.storage import load_store, save_store

_PRIORITIES_KEY = "__priorities__"
_VALID_LEVELS = ("low", "medium", "high", "critical")


def _priorities_map(store_path, password: str) -> Dict[str, str]:
    store = load_store(store_path, password)
    return store.get(_PRIORITIES_KEY, {})


def set_priority(
    store_path, password: str, project: str, level: str
) -> None:
    """Assign a priority level to a project."""
    if level not in _VALID_LEVELS:
        raise ValueError(
            f"Invalid priority '{level}'. Choose from: {', '.join(_VALID_LEVELS)}"
        )
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' does not exist.")
    priorities = store.setdefault(_PRIORITIES_KEY, {})
    priorities[project] = level
    save_store(store_path, password, store)


def get_priority(
    store_path, password: str, project: str
) -> Optional[str]:
    """Return the priority level for a project, or None if unset."""
    return _priorities_map(store_path, password).get(project)


def remove_priority(store_path, password: str, project: str) -> bool:
    """Remove the priority for a project. Returns True if it existed."""
    store = load_store(store_path, password)
    priorities = store.get(_PRIORITIES_KEY, {})
    existed = project in priorities
    if existed:
        del priorities[project]
        store[_PRIORITIES_KEY] = priorities
        save_store(store_path, password, store)
    return existed


def list_priorities(store_path, password: str) -> Dict[str, str]:
    """Return a mapping of project -> priority level for all assigned projects."""
    return dict(_priorities_map(store_path, password))


def projects_by_priority(
    store_path, password: str, level: str
) -> List[str]:
    """Return all projects with the given priority level."""
    if level not in _VALID_LEVELS:
        raise ValueError(
            f"Invalid priority '{level}'. Choose from: {', '.join(_VALID_LEVELS)}"
        )
    return [
        project
        for project, lvl in _priorities_map(store_path, password).items()
        if lvl == level
    ]
