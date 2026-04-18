"""Project pinning — mark projects as pinned so they appear at the top of listings."""
from __future__ import annotations

from envault.storage import load_store, save_store

_PINS_KEY = "__pins__"


def _pins(store: dict) -> list[str]:
    return store.get(_PINS_KEY, [])


def pin_project(store_path, password: str, project: str) -> None:
    """Pin *project*. Raises KeyError if the project does not exist."""
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    pins = _pins(store)
    if project not in pins:
        pins.append(project)
    store[_PINS_KEY] = pins
    save_store(store_path, password, store)


def unpin_project(store_path, password: str, project: str) -> None:
    """Unpin *project*. Silent no-op if project is not pinned."""
    store = load_store(store_path, password)
    pins = _pins(store)
    if project in pins:
        pins.remove(project)
    store[_PINS_KEY] = pins
    save_store(store_path, password, store)


def list_pinned(store_path, password: str) -> list[str]:
    """Return list of pinned project names."""
    store = load_store(store_path, password)
    return list(_pins(store))


def is_pinned(store_path, password: str, project: str) -> bool:
    store = load_store(store_path, password)
    return project in _pins(store)
