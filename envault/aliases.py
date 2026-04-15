"""Project alias management for envault.

Allows users to assign short aliases to project names for convenience.
"""

from __future__ import annotations

from envault.storage import load_store, save_store

_ALIAS_KEY = "__aliases__"


def _alias_map(store: dict) -> dict:
    """Return the alias -> project mapping from the store root."""
    return store.get(_ALIAS_KEY, {})


def set_alias(store_path: str, password: str, alias: str, project: str) -> None:
    """Bind *alias* to *project*. Raises KeyError if project does not exist."""
    store = load_store(store_path, password)
    projects = {k for k in store if not k.startswith("__")}
    if project not in projects:
        raise KeyError(f"Project '{project}' not found.")
    aliases = _alias_map(store)
    aliases[alias] = project
    store[_ALIAS_KEY] = aliases
    save_store(store_path, password, store)


def remove_alias(store_path: str, password: str, alias: str) -> None:
    """Remove *alias*. Raises KeyError if alias does not exist."""
    store = load_store(store_path, password)
    aliases = _alias_map(store)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found.")
    del aliases[alias]
    store[_ALIAS_KEY] = aliases
    save_store(store_path, password, store)


def resolve_alias(store_path: str, password: str, alias: str) -> str:
    """Return the project name for *alias*, or *alias* itself if not mapped."""
    store = load_store(store_path, password)
    return _alias_map(store).get(alias, alias)


def list_aliases(store_path: str, password: str) -> dict[str, str]:
    """Return a copy of the full alias -> project mapping."""
    store = load_store(store_path, password)
    return dict(_alias_map(store))
