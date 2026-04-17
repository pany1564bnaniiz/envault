"""Per-project notes stored inside the encrypted vault."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envault.storage import load_store, save_store

_NOTES_KEY = "__notes__"


def _notes_map(store: dict) -> dict:
    return store.setdefault(_NOTES_KEY, {})


def set_note(store_path, password: str, project: str, text: str) -> None:
    """Set or replace the note for *project*."""
    store = load_store(store_path, password)
    projects = {k for k in store if not k.startswith("__")}
    if project not in projects:
        raise KeyError(f"Project '{project}' not found.")
    _notes_map(store)[project] = {
        "text": text,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_store(store_path, password, store)


def get_note(store_path, password: str, project: str) -> Optional[dict]:
    """Return the note dict for *project*, or None if not set."""
    store = load_store(store_path, password)
    return _notes_map(store).get(project)


def delete_note(store_path, password: str, project: str) -> bool:
    """Delete the note for *project*. Returns True if a note existed."""
    store = load_store(store_path, password)
    removed = _notes_map(store).pop(project, None)
    save_store(store_path, password, store)
    return removed is not None


def list_notes(store_path, password: str) -> dict[str, dict]:
    """Return all project notes as {project: note_dict}."""
    store = load_store(store_path, password)
    return dict(_notes_map(store))
