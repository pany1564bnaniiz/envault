"""Retention policies: automatically expire projects after a set number of days."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from envault.storage import load_store, save_store

_RETENTION_KEY = "__retentions__"


def _retentions_map(store: dict) -> dict:
    return store.setdefault(_RETENTION_KEY, {})


def set_retention(
    store_path: str,
    password: str,
    project: str,
    days: int,
) -> dict:
    """Set a retention policy (in days) for *project*."""
    if days <= 0:
        raise ValueError("days must be a positive integer")
    store = load_store(store_path, password)
    if project not in store and project != _RETENTION_KEY:
        active = {k for k in store if not k.startswith("__")}
        if project not in active:
            raise KeyError(f"Project '{project}' does not exist")
    expires_at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    entry = {"days": days, "expires_at": expires_at}
    _retentions_map(store)[project] = entry
    save_store(store_path, password, store)
    return entry


def get_retention(store_path: str, password: str, project: str) -> Optional[dict]:
    """Return the retention entry for *project*, or None if not set."""
    store = load_store(store_path, password)
    return _retentions_map(store).get(project)


def delete_retention(store_path: str, password: str, project: str) -> bool:
    """Remove the retention policy for *project*. Returns True if it existed."""
    store = load_store(store_path, password)
    retentions = _retentions_map(store)
    if project not in retentions:
        return False
    del retentions[project]
    save_store(store_path, password, store)
    return True


def list_retentions(store_path: str, password: str) -> list[dict]:
    """Return all retention policies sorted by expiry date."""
    store = load_store(store_path, password)
    retentions = _retentions_map(store)
    result = [
        {"project": proj, **data}
        for proj, data in retentions.items()
    ]
    result.sort(key=lambda r: r["expires_at"])
    return result


def expired_projects(store_path: str, password: str) -> list[str]:
    """Return names of projects whose retention period has elapsed."""
    now = datetime.now(timezone.utc).isoformat()
    store = load_store(store_path, password)
    retentions = _retentions_map(store)
    return [
        proj
        for proj, data in retentions.items()
        if data.get("expires_at", "") <= now
    ]
