"""Snapshot support: save and restore named env snapshots per project."""

from __future__ import annotations

from typing import Dict, List

from envault.storage import load_store, save_store

_SNAPSHOT_PREFIX = "__snapshot__"


def _snapshot_key(name: str) -> str:
    return f"{_SNAPSHOT_PREFIX}{name}"


def save_snapshot(
    project: str,
    name: str,
    password: str,
    store_path=None,
) -> None:
    """Save the current env of *project* as snapshot *name*."""
    kwargs = {"store_path": store_path} if store_path else {}
    store = load_store(password, **kwargs)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    snapshot_data = dict(store[project])  # shallow copy of current env vars
    snapshots = store.setdefault("__snapshots__", {})
    project_snaps = snapshots.setdefault(project, {})
    project_snaps[name] = snapshot_data
    save_store(store, password, **kwargs)


def list_snapshots(project: str, password: str, store_path=None) -> List[str]:
    """Return the names of all snapshots for *project*."""
    kwargs = {"store_path": store_path} if store_path else {}
    store = load_store(password, **kwargs)
    return list(store.get("__snapshots__", {}).get(project, {}).keys())


def load_snapshot(
    project: str,
    name: str,
    password: str,
    store_path=None,
) -> Dict[str, str]:
    """Return the env dict stored in snapshot *name* for *project*."""
    kwargs = {"store_path": store_path} if store_path else {}
    store = load_store(password, **kwargs)
    try:
        return dict(store["__snapshots__"][project][name])
    except KeyError:
        raise KeyError(f"Snapshot '{name}' not found for project '{project}'.")


def delete_snapshot(
    project: str,
    name: str,
    password: str,
    store_path=None,
) -> None:
    """Delete snapshot *name* from *project*."""
    kwargs = {"store_path": store_path} if store_path else {}
    store = load_store(password, **kwargs)
    try:
        del store["__snapshots__"][project][name]
    except KeyError:
        raise KeyError(f"Snapshot '{name}' not found for project '{project}'.")
    save_store(store, password, **kwargs)
