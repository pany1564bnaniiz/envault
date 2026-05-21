"""Deadline tracking for envault projects."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envault.storage import load_store, save_store

_DEADLINES_KEY = "__deadlines__"


def _deadlines_map(store: dict) -> dict:
    return store.setdefault(_DEADLINES_KEY, {})


def set_deadline(
    store_path,
    password: str,
    project: str,
    due: datetime,
    label: str = "",
) -> None:
    """Attach a deadline to a project."""
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' does not exist.")
    dm = _deadlines_map(store)
    dm[project] = {
        "due": due.isoformat(),
        "label": label,
    }
    save_store(store_path, password, store)


def get_deadline(store_path, password: str, project: str) -> Optional[dict]:
    """Return deadline info for a project, or None if not set."""
    store = load_store(store_path, password)
    return _deadlines_map(store).get(project)


def delete_deadline(store_path, password: str, project: str) -> None:
    """Remove the deadline from a project."""
    store = load_store(store_path, password)
    dm = _deadlines_map(store)
    if project not in dm:
        raise KeyError(f"No deadline set for project '{project}'.")
    del dm[project]
    save_store(store_path, password, store)


def overdue_projects(store_path, password: str) -> list[dict]:
    """Return all projects whose deadline has passed."""
    store = load_store(store_path, password)
    now = datetime.now(tz=timezone.utc)
    results = []
    for project, info in _deadlines_map(store).items():
        due = datetime.fromisoformat(info["due"])
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        if due < now:
            results.append({"project": project, "due": info["due"], "label": info["label"]})
    return results


def list_deadlines(store_path, password: str) -> list[dict]:
    """Return all deadline entries sorted by due date."""
    store = load_store(store_path, password)
    entries = [
        {"project": p, "due": v["due"], "label": v["label"]}
        for p, v in _deadlines_map(store).items()
    ]
    return sorted(entries, key=lambda e: e["due"])
