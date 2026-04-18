"""Per-key change history tracking for envault projects."""
from __future__ import annotations
import time
from typing import Any
from envault.storage import load_store, save_store

_HISTORY_PREFIX = "__history__"
_MAX_ENTRIES = 50


def _history_key(project: str) -> str:
    return f"{_HISTORY_PREFIX}{project}"


def record_change(
    store_path: str,
    password: str,
    project: str,
    key: str,
    old_value: str | None,
    new_value: str | None,
    action: str,
) -> None:
    """Append a history entry for a key change."""
    store = load_store(store_path, password)
    hk = _history_key(project)
    history: list[dict[str, Any]] = store.get(hk, [])
    history.append({
        "key": key,
        "action": action,
        "old_value": old_value,
        "new_value": new_value,
        "timestamp": time.time(),
    })
    if len(history) > _MAX_ENTRIES:
        history = history[-_MAX_ENTRIES:]
    store[hk] = history
    save_store(store_path, password, store)


def get_history(
    store_path: str,
    password: str,
    project: str,
    key: str | None = None,
) -> list[dict[str, Any]]:
    """Return history entries, optionally filtered by key."""
    store = load_store(store_path, password)
    history: list[dict[str, Any]] = store.get(_history_key(project), [])
    if key is not None:
        history = [e for e in history if e["key"] == key]
    return history


def clear_history(store_path: str, password: str, project: str) -> None:
    """Remove all history for a project."""
    store = load_store(store_path, password)
    store.pop(_history_key(project), None)
    save_store(store_path, password, store)
