"""Project subscription system — track which users subscribe to a project for change notifications."""

from __future__ import annotations

from typing import List

from envault.storage import load_store, save_store

_SUBS_KEY = "__subscriptions__"


def _subs_map(store: dict) -> dict:
    return store.setdefault(_SUBS_KEY, {})


def subscribe(store_path, password: str, project: str, user: str) -> None:
    """Subscribe *user* to *project*. Raises KeyError if project does not exist."""
    store = load_store(store_path, password)
    if project not in store or project == _SUBS_KEY:
        raise KeyError(f"Project '{project}' not found.")
    subs = _subs_map(store)
    current: List[str] = subs.get(project, [])
    if user not in current:
        current.append(user)
    subs[project] = current
    save_store(store_path, password, store)


def unsubscribe(store_path, password: str, project: str, user: str) -> None:
    """Remove *user* from *project* subscribers. Silent if not subscribed."""
    store = load_store(store_path, password)
    subs = _subs_map(store)
    current: List[str] = subs.get(project, [])
    subs[project] = [u for u in current if u != user]
    save_store(store_path, password, store)


def list_subscribers(store_path, password: str, project: str) -> List[str]:
    """Return sorted list of users subscribed to *project*."""
    store = load_store(store_path, password)
    subs = _subs_map(store)
    return sorted(subs.get(project, []))


def subscriptions_for(store_path, password: str, user: str) -> List[str]:
    """Return sorted list of projects *user* is subscribed to."""
    store = load_store(store_path, password)
    subs = _subs_map(store)
    return sorted(project for project, users in subs.items() if user in users)
