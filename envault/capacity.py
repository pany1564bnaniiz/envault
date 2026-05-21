"""Capacity tracking: set and enforce max key limits per project."""

from __future__ import annotations

from envault.storage import load_store, save_store
from envault.projects import get_all_env

_CAPACITY_KEY = "__capacity__"


def _capacity_map(store: dict) -> dict:
    return store.setdefault(_CAPACITY_KEY, {})


def set_capacity(store_path, password: str, project: str, max_keys: int) -> None:
    """Set the maximum number of keys allowed in *project*."""
    if max_keys < 1:
        raise ValueError("max_keys must be a positive integer")
    store = load_store(store_path, password)
    if project not in store and project != _CAPACITY_KEY:
        active = {k: v for k, v in store.items() if not k.startswith("__")}
        if project not in active:
            raise KeyError(f"Project '{project}' does not exist")
    _capacity_map(store)[project] = max_keys
    save_store(store_path, password, store)


def get_capacity(store_path, password: str, project: str) -> int | None:
    """Return the capacity limit for *project*, or None if not set."""
    store = load_store(store_path, password)
    return _capacity_map(store).get(project)


def remove_capacity(store_path, password: str, project: str) -> bool:
    """Remove the capacity limit for *project*. Returns True if removed."""
    store = load_store(store_path, password)
    cmap = _capacity_map(store)
    if project not in cmap:
        return False
    del cmap[project]
    save_store(store_path, password, store)
    return True


def check_capacity(store_path, password: str, project: str) -> dict:
    """Return usage info: {limit, used, available, exceeded}."""
    limit = get_capacity(store_path, password, project)
    env = get_all_env(store_path, password, project)
    used = len(env)
    if limit is None:
        return {"limit": None, "used": used, "available": None, "exceeded": False}
    return {
        "limit": limit,
        "used": used,
        "available": max(0, limit - used),
        "exceeded": used > limit,
    }


def list_capacities(store_path, password: str) -> list[dict]:
    """Return a sorted list of all capacity entries."""
    store = load_store(store_path, password)
    cmap = _capacity_map(store)
    return sorted(
        [{"project": p, "max_keys": v} for p, v in cmap.items()],
        key=lambda x: x["project"],
    )
