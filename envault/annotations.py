"""Per-key annotations: attach short notes to individual env keys within a project."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envault.storage import load_store, save_store
from envault.projects import get_all_env

_ANNOTATIONS_KEY = "__annotations__"


def _annotations_map(store: dict, project: str) -> dict:
    return store.setdefault(project, {}).setdefault(_ANNOTATIONS_KEY, {})


def set_annotation(
    store_path: str,
    password: str,
    project: str,
    key: str,
    note: str,
) -> dict:
    """Attach an annotation to *key* inside *project*. Returns the annotation entry."""
    store = load_store(store_path, password)
    env = get_all_env(store_path, password, project)  # validates project exists
    if key not in env:
        raise KeyError(f"Key '{key}' not found in project '{project}'")
    annotations = _annotations_map(store, project)
    entry = {"note": note, "updated_at": datetime.now(timezone.utc).isoformat()}
    annotations[key] = entry
    save_store(store_path, password, store)
    return entry


def get_annotation(
    store_path: str,
    password: str,
    project: str,
    key: str,
) -> Optional[dict]:
    """Return the annotation for *key*, or None if not set."""
    store = load_store(store_path, password)
    return _annotations_map(store, project).get(key)


def delete_annotation(
    store_path: str,
    password: str,
    project: str,
    key: str,
) -> bool:
    """Remove annotation for *key*. Returns True if it existed, False otherwise."""
    store = load_store(store_path, password)
    annotations = _annotations_map(store, project)
    if key not in annotations:
        return False
    del annotations[key]
    save_store(store_path, password, store)
    return True


def list_annotations(
    store_path: str,
    password: str,
    project: str,
) -> dict:
    """Return all annotations for *project* as {key: entry}."""
    store = load_store(store_path, password)
    return dict(_annotations_map(store, project))
