"""Per-project key count quotas for envault."""

from __future__ import annotations

from typing import Optional

from envault.storage import load_store, save_store
from envault.projects import get_all_env

_QUOTA_KEY = "__quota__"
_DEFAULT_QUOTA = 100


def _quota_map(store: dict) -> dict:
    """Return the quota sub-dict from the store."""
    if _QUOTA_KEY not in store:
        store[_QUOTA_KEY] = {}
    return store[_QUOTA_KEY]


def set_quota(store_path: str, password: str, project: str, limit: int) -> None:
    """Set the maximum number of keys allowed for *project*.

    Raises ValueError if *limit* is not a positive integer.
    """
    if limit < 1:
        raise ValueError(f"Quota limit must be a positive integer, got {limit}.")
    store = load_store(store_path, password)
    active_projects = [
        k for k in store if not k.startswith("__")
    ]
    if project not in active_projects:
        raise KeyError(f"Project '{project}' does not exist.")
    _quota_map(store)[project] = limit
    save_store(store_path, password, store)


def get_quota(store_path: str, password: str, project: str) -> Optional[int]:
    """Return the quota for *project*, or None if no quota is set."""
    store = load_store(store_path, password)
    return _quota_map(store).get(project)


def remove_quota(store_path: str, password: str, project: str) -> None:
    """Remove the quota for *project* (no-op if not set)."""
    store = load_store(store_path, password)
    _quota_map(store).pop(project, None)
    save_store(store_path, password, store)


def check_quota(store_path: str, password: str, project: str) -> dict:
    """Return a dict with quota info for *project*.

    Keys: ``limit`` (int or None), ``used`` (int), ``remaining`` (int or None),
    ``exceeded`` (bool).
    """
    store = load_store(store_path, password)
    limit = _quota_map(store).get(project)
    env = get_all_env(store_path, password, project) if project in store else {}
    used = len(env)
    remaining = (limit - used) if limit is not None else None
    exceeded = (used > limit) if limit is not None else False
    return {
        "limit": limit,
        "used": used,
        "remaining": remaining,
        "exceeded": exceeded,
    }


def enforce_quota(store_path: str, password: str, project: str) -> None:
    """Raise PermissionError if the project's key count exceeds its quota."""
    info = check_quota(store_path, password, project)
    if info["exceeded"]:
        raise PermissionError(
            f"Project '{project}' has exceeded its quota of {info['limit']} keys "
            f"({info['used']} keys stored)."
        )
