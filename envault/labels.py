"""Project labels — arbitrary colour-tagged metadata for organising projects."""
from __future__ import annotations

from typing import Dict, List

from envault.storage import load_store, save_store

_LABELS_KEY = "__labels__"

# Allowed colours (kept small and explicit for CLI display)
VALID_COLOURS = {"red", "green", "blue", "yellow", "cyan", "magenta", "white", "grey"}


def _labels_map(store: dict) -> dict:
    """Return the mutable labels sub-dict from *store*."""
    if _LABELS_KEY not in store:
        store[_LABELS_KEY] = {}
    return store[_LABELS_KEY]


def set_label(store_path: str, password: str, project: str, colour: str) -> None:
    """Attach *colour* label to *project*.

    Raises
    ------
    KeyError  – project does not exist.
    ValueError – colour is not in VALID_COLOURS.
    """
    if colour not in VALID_COLOURS:
        raise ValueError(f"Invalid colour '{colour}'. Choose from: {sorted(VALID_COLOURS)}")
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    _labels_map(store)[project] = colour
    save_store(store_path, password, store)


def get_label(store_path: str, password: str, project: str) -> str | None:
    """Return the colour label for *project*, or *None* if unset."""
    store = load_store(store_path, password)
    return _labels_map(store).get(project)


def remove_label(store_path: str, password: str, project: str) -> None:
    """Remove the label from *project* (no-op if not labelled)."""
    store = load_store(store_path, password)
    _labels_map(store).pop(project, None)
    save_store(store_path, password, store)


def list_labels(store_path: str, password: str) -> Dict[str, str]:
    """Return a mapping of {project: colour} for all labelled projects."""
    store = load_store(store_path, password)
    return dict(_labels_map(store))


def projects_by_colour(store_path: str, password: str, colour: str) -> List[str]:
    """Return sorted list of projects that carry *colour* label."""
    mapping = list_labels(store_path, password)
    return sorted(p for p, c in mapping.items() if c == colour)
