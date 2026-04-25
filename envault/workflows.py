"""Workflow support: named sequences of CLI-style operations applied to a project."""
from __future__ import annotations

from typing import Any

from envault.storage import load_store, save_store

_WORKFLOWS_KEY = "__workflows__"

VALID_STEPS = {"set", "delete", "clone", "snapshot", "export"}


def _workflows_map(store: dict) -> dict:
    return store.setdefault(_WORKFLOWS_KEY, {})


def save_workflow(
    store_path: str,
    password: str,
    name: str,
    steps: list[dict[str, Any]],
) -> None:
    """Persist a named workflow (list of step dicts) to the store."""
    if not name:
        raise ValueError("Workflow name must not be empty.")
    for step in steps:
        action = step.get("action")
        if action not in VALID_STEPS:
            raise ValueError(f"Invalid workflow action: {action!r}. Must be one of {sorted(VALID_STEPS)}.")
    store = load_store(store_path, password)
    _workflows_map(store)[name] = steps
    save_store(store_path, password, store)


def load_workflow(
    store_path: str,
    password: str,
    name: str,
) -> list[dict[str, Any]]:
    """Return the steps for a named workflow, raising KeyError if absent."""
    store = load_store(store_path, password)
    wf = _workflows_map(store)
    if name not in wf:
        raise KeyError(f"Workflow not found: {name!r}")
    return wf[name]


def list_workflows(store_path: str, password: str) -> list[str]:
    """Return sorted list of workflow names."""
    store = load_store(store_path, password)
    return sorted(_workflows_map(store).keys())


def delete_workflow(store_path: str, password: str, name: str) -> None:
    """Remove a named workflow; raises KeyError if it doesn't exist."""
    store = load_store(store_path, password)
    wf = _workflows_map(store)
    if name not in wf:
        raise KeyError(f"Workflow not found: {name!r}")
    del wf[name]
    save_store(store_path, password, store)
