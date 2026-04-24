"""Archive and restore projects — soft-delete with recovery support."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from envault.storage import load_store, save_store

_ARCHIVE_NS = "__archive__"


def _archive_map(store: dict) -> dict:
    return store.setdefault(_ARCHIVE_NS, {})


def archive_project(store_path: str, password: str, project: str) -> None:
    """Move *project* into the archive namespace.

    Raises KeyError if the project does not exist or is already archived.
    """
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    if project.startswith("__"):
        raise KeyError(f"Cannot archive internal namespace '{project}'.")

    archive = _archive_map(store)
    if project in archive:
        raise KeyError(f"Project '{project}' is already archived.")

    archive[project] = {
        "env": store.pop(project),
        "archived_at": datetime.now(timezone.utc).isoformat(),
    }
    save_store(store_path, password, store)


def restore_project(store_path: str, password: str, project: str) -> None:
    """Restore an archived project back to active storage.

    Raises KeyError if the project is not in the archive.
    """
    store = load_store(store_path, password)
    archive = _archive_map(store)
    if project not in archive:
        raise KeyError(f"Project '{project}' is not archived.")

    store[project] = archive.pop(project)["env"]
    if not archive:
        del store[_ARCHIVE_NS]
    save_store(store_path, password, store)


def list_archived(store_path: str, password: str) -> list[dict[str, Any]]:
    """Return a list of archived project metadata dicts.

    Each dict contains 'project' and 'archived_at'.
    """
    store = load_store(store_path, password)
    archive = store.get(_ARCHIVE_NS, {})
    return [
        {"project": name, "archived_at": meta["archived_at"]}
        for name, meta in sorted(archive.items())
    ]


def purge_archived(store_path: str, password: str, project: str) -> None:
    """Permanently delete an archived project.

    Raises KeyError if the project is not in the archive.
    """
    store = load_store(store_path, password)
    archive = _archive_map(store)
    if project not in archive:
        raise KeyError(f"Project '{project}' is not archived.")

    del archive[project]
    if not archive:
        del store[_ARCHIVE_NS]
    save_store(store_path, password, store)
