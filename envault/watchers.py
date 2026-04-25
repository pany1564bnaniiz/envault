"""Project watcher registry — subscribe to change notifications for projects."""

from __future__ import annotations

from typing import List, Dict

from envault.storage import load_store, save_store

_WATCHERS_KEY = "__watchers__"


def _watchers_map(store_path, password: str) -> Dict[str, List[str]]:
    store = load_store(store_path, password)
    return store.get(_WATCHERS_KEY, {})


def add_watcher(store_path, password: str, project: str, email: str) -> None:
    """Add *email* as a watcher for *project*."""
    store = load_store(store_path, password)
    if project not in store and project != _WATCHERS_KEY:
        raise KeyError(f"Project '{project}' does not exist.")
    watchers: Dict[str, List[str]] = store.setdefault(_WATCHERS_KEY, {})
    existing: List[str] = watchers.setdefault(project, [])
    if email not in existing:
        existing.append(email)
    save_store(store_path, password, store)


def remove_watcher(store_path, password: str, project: str, email: str) -> bool:
    """Remove *email* from watchers for *project*. Returns True if removed."""
    store = load_store(store_path, password)
    watchers: Dict[str, List[str]] = store.get(_WATCHERS_KEY, {})
    project_watchers = watchers.get(project, [])
    if email not in project_watchers:
        return False
    project_watchers.remove(email)
    watchers[project] = project_watchers
    store[_WATCHERS_KEY] = watchers
    save_store(store_path, password, store)
    return True


def list_watchers(store_path, password: str, project: str) -> List[str]:
    """Return all watcher emails for *project*."""
    wmap = _watchers_map(store_path, password)
    return list(wmap.get(project, []))


def watched_projects(store_path, password: str, email: str) -> List[str]:
    """Return all projects that *email* is watching."""
    wmap = _watchers_map(store_path, password)
    return [proj for proj, emails in wmap.items() if email in emails]
