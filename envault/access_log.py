"""Per-project access log: track who read/wrote which keys and when."""

from __future__ import annotations

import datetime
from typing import List, Optional

from envault.storage import load_store, save_store

_ACCESS_LOG_KEY = "__access_log__"


def _log_map(store: dict) -> dict:
    return store.setdefault(_ACCESS_LOG_KEY, {})


def record_access(
    store_path: str,
    password: str,
    project: str,
    action: str,
    key: Optional[str] = None,
    actor: str = "local",
) -> None:
    """Append an access entry for *project*.

    Args:
        store_path: Path to the encrypted store file.
        password:   Vault password.
        project:    Target project name.
        action:     One of 'read', 'write', 'delete'.
        key:        Optional env-var key involved in the action.
        actor:      Identifier for who performed the action (default 'local').
    """
    if action not in {"read", "write", "delete"}:
        raise ValueError(f"Invalid action '{action}'; must be read, write, or delete.")

    store = load_store(store_path, password)
    log = _log_map(store)
    entries = log.setdefault(project, [])
    entries.append(
        {
            "ts": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "action": action,
            "key": key,
            "actor": actor,
        }
    )
    save_store(store_path, password, store)


def get_access_log(
    store_path: str,
    password: str,
    project: str,
    action: Optional[str] = None,
) -> List[dict]:
    """Return access log entries for *project*, optionally filtered by *action*."""
    store = load_store(store_path, password)
    entries = _log_map(store).get(project, [])
    if action:
        entries = [e for e in entries if e["action"] == action]
    return list(entries)


def clear_access_log(store_path: str, password: str, project: str) -> int:
    """Remove all access log entries for *project*. Returns count of removed entries."""
    store = load_store(store_path, password)
    log = _log_map(store)
    removed = len(log.pop(project, []))
    save_store(store_path, password, store)
    return removed
