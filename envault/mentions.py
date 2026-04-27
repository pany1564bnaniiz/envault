"""mentions.py — track @user mentions attached to projects."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Dict

from envault.storage import load_store, save_store

_MENTIONS_KEY = "__mentions__"


def _mentions_map(store: dict) -> dict:
    return store.setdefault(_MENTIONS_KEY, {})


def add_mention(
    store_path: str,
    password: str,
    project: str,
    user: str,
    message: str = "",
) -> dict:
    """Add a mention of *user* on *project*, returning the new entry."""
    store = load_store(store_path, password)
    projects = store.get("projects", {})
    if project not in projects:
        raise KeyError(f"Project '{project}' not found.")

    mentions = _mentions_map(store)
    bucket = mentions.setdefault(project, [])

    entry = {
        "user": user,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    bucket.append(entry)
    save_store(store_path, password, store)
    return entry


def list_mentions(
    store_path: str,
    password: str,
    project: str,
) -> List[Dict]:
    """Return all mention entries for *project* in chronological order."""
    store = load_store(store_path, password)
    projects = store.get("projects", {})
    if project not in projects:
        raise KeyError(f"Project '{project}' not found.")
    return list(_mentions_map(store).get(project, []))


def mentions_for_user(
    store_path: str,
    password: str,
    user: str,
) -> Dict[str, List[Dict]]:
    """Return a mapping of project -> mentions that reference *user*."""
    store = load_store(store_path, password)
    result: Dict[str, List[Dict]] = {}
    for project, entries in _mentions_map(store).items():
        hits = [e for e in entries if e.get("user") == user]
        if hits:
            result[project] = hits
    return result


def clear_mentions(
    store_path: str,
    password: str,
    project: str,
) -> int:
    """Remove all mentions for *project*. Returns count removed."""
    store = load_store(store_path, password)
    projects = store.get("projects", {})
    if project not in projects:
        raise KeyError(f"Project '{project}' not found.")
    mentions = _mentions_map(store)
    removed = len(mentions.pop(project, []))
    save_store(store_path, password, store)
    return removed
