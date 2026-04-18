"""Favorites: mark projects as favorite for quick access."""
from __future__ import annotations

from envault.storage import load_store, save_store

_FAVORITES_KEY = "__favorites__"


def _favorites(store: dict) -> dict:
    return store.setdefault(_FAVORITES_KEY, {})


def add_favorite(store_path, password: str, project: str) -> None:
    store = load_store(store_path, password)
    projects = {k for k in store if not k.startswith("__")}
    if project not in projects:
        raise KeyError(f"Project '{project}' not found.")
    _favorites(store)[project] = True
    save_store(store_path, password, store)


def remove_favorite(store_path, password: str, project: str) -> None:
    store = load_store(store_path, password)
    favs = _favorites(store)
    if project not in favs:
        raise KeyError(f"Project '{project}' is not a favorite.")
    del favs[project]
    save_store(store_path, password, store)


def list_favorites(store_path, password: str) -> list[str]:
    store = load_store(store_path, password)
    return sorted(_favorites(store).keys())


def is_favorite(store_path, password: str, project: str) -> bool:
    store = load_store(store_path, password)
    return project in _favorites(store)
