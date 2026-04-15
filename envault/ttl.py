"""TTL (time-to-live) support for env keys — mark keys as expiring and check/purge them."""

from __future__ import annotations

import time
from typing import Optional

from envault.storage import load_store, save_store

_TTL_META_KEY = "__ttl__"


def _ttl_map(store: dict, project: str) -> dict:
    """Return the TTL metadata dict for a project (mutable reference)."""
    project_data = store.get(project, {})
    if _TTL_META_KEY not in project_data:
        project_data[_TTL_META_KEY] = {}
    return project_data[_TTL_META_KEY]


def set_ttl(store_path: str, password: str, project: str, key: str, ttl_seconds: int) -> None:
    """Attach a TTL (in seconds from now) to an existing env key."""
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    if key not in store[project]:
        raise KeyError(f"Key '{key}' not found in project '{project}'.")
    expires_at = time.time() + ttl_seconds
    _ttl_map(store, project)[key] = expires_at
    save_store(store_path, password, store)


def get_ttl(store_path: str, password: str, project: str, key: str) -> Optional[float]:
    """Return the expiry timestamp for a key, or None if no TTL is set."""
    store = load_store(store_path, password)
    return _ttl_map(store, project).get(key)


def purge_expired(store_path: str, password: str, project: str) -> list[str]:
    """Remove all expired keys from a project. Returns list of purged key names."""
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")

    now = time.time()
    ttl_map = _ttl_map(store, project)
    expired = [k for k, exp in ttl_map.items() if exp <= now]

    for key in expired:
        store[project].pop(key, None)
        ttl_map.pop(key, None)

    if expired:
        save_store(store_path, password, store)

    return expired


def list_expiring(store_path: str, password: str, project: str) -> dict[str, float]:
    """Return a mapping of key -> expiry timestamp for all keys with a TTL."""
    store = load_store(store_path, password)
    return dict(_ttl_map(store, project))
