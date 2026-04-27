"""Per-key comments for env variables within a project."""

from __future__ import annotations

from typing import Optional

from envault.storage import load_store, save_store
from envault.projects import get_all_env

_COMMENTS_KEY = "__comments__"


def _comments_map(store: dict, project: str) -> dict:
    return store.get(project, {}).get(_COMMENTS_KEY, {})


def set_comment(
    store_path: str,
    password: str,
    project: str,
    key: str,
    comment: str,
) -> None:
    """Attach a comment to *key* inside *project*."""
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    # Verify the key actually exists in the project env.
    env = get_all_env(store_path, password, project)
    if key not in env:
        raise KeyError(f"Key '{key}' not found in project '{project}'.")
    comments = store[project].setdefault(_COMMENTS_KEY, {})
    comments[key] = comment
    save_store(store_path, password, store)


def get_comment(
    store_path: str,
    password: str,
    project: str,
    key: str,
) -> Optional[str]:
    """Return the comment for *key*, or ``None`` if unset."""
    store = load_store(store_path, password)
    return _comments_map(store, project).get(key)


def delete_comment(
    store_path: str,
    password: str,
    project: str,
    key: str,
) -> bool:
    """Remove the comment for *key*.  Returns True if a comment existed."""
    store = load_store(store_path, password)
    comments = store.get(project, {}).get(_COMMENTS_KEY, {})
    if key not in comments:
        return False
    del comments[key]
    save_store(store_path, password, store)
    return True


def list_comments(
    store_path: str,
    password: str,
    project: str,
) -> dict[str, str]:
    """Return all key→comment mappings for *project*."""
    store = load_store(store_path, password)
    return dict(_comments_map(store, project))
