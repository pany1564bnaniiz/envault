"""Bookmarks: save named references to specific project+key pairs for quick access."""

from __future__ import annotations

from typing import Optional

from envault.storage import load_store, save_store

_BOOKMARKS_KEY = "__bookmarks__"


def _bookmarks_map(store: dict) -> dict:
    return store.setdefault(_BOOKMARKS_KEY, {})


def add_bookmark(
    store_path: str,
    password: str,
    name: str,
    project: str,
    key: str,
    description: str = "",
) -> None:
    """Save a named bookmark pointing to project/key."""
    store = load_store(store_path, password)
    if project not in store or project == _BOOKMARKS_KEY:
        raise KeyError(f"Project '{project}' does not exist.")
    bm = _bookmarks_map(store)
    bm[name] = {"project": project, "key": key, "description": description}
    save_store(store_path, password, store)


def remove_bookmark(store_path: str, password: str, name: str) -> None:
    """Delete a bookmark by name."""
    store = load_store(store_path, password)
    bm = _bookmarks_map(store)
    if name not in bm:
        raise KeyError(f"Bookmark '{name}' does not exist.")
    del bm[name]
    save_store(store_path, password, store)


def get_bookmark(store_path: str, password: str, name: str) -> dict:
    """Return the bookmark entry for *name*."""
    store = load_store(store_path, password)
    bm = _bookmarks_map(store)
    if name not in bm:
        raise KeyError(f"Bookmark '{name}' does not exist.")
    return dict(bm[name])


def list_bookmarks(store_path: str, password: str) -> list[dict]:
    """Return all bookmarks sorted by name."""
    store = load_store(store_path, password)
    bm = _bookmarks_map(store)
    return [
        {"name": n, **v}
        for n, v in sorted(bm.items())
    ]


def resolve_bookmark(store_path: str, password: str, name: str) -> Optional[str]:
    """Return the current value of the key referenced by *name*, or None if missing."""
    from envault.projects import get_env

    entry = get_bookmark(store_path, password, name)
    try:
        return get_env(store_path, password, entry["project"], entry["key"])
    except KeyError:
        return None
