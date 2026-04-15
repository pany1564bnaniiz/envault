"""Project management: add, get, update, and remove env entries per project."""

from __future__ import annotations

from typing import Dict

from envault.storage import load_store, save_store


def set_env(project: str, key: str, value: str, password: str) -> None:
    """Set (add or update) a single env variable for a project."""
    store = load_store(password)
    if project not in store:
        store[project] = {}
    store[project][key] = value
    save_store(store, password)


def get_env(project: str, key: str, password: str) -> str:
    """Retrieve a single env variable for a project.

    Raises KeyError if the project or key does not exist.
    """
    store = load_store(password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    if key not in store[project]:
        raise KeyError(f"Key '{key}' not found in project '{project}'.")
    return store[project][key]


def get_all_env(project: str, password: str) -> Dict[str, str]:
    """Return all env variables for a project as a dict.

    Raises KeyError if the project does not exist.
    """
    store = load_store(password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    return dict(store[project])


def delete_env(project: str, key: str, password: str) -> None:
    """Delete a single env variable from a project.

    Raises KeyError if the project or key does not exist.
    """
    store = load_store(password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    if key not in store[project]:
        raise KeyError(f"Key '{key}' not found in project '{project}'.")
    del store[project][key]
    save_store(store, password)


def delete_project(project: str, password: str) -> None:
    """Remove an entire project and all its env variables.

    Raises KeyError if the project does not exist.
    """
    store = load_store(password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    del store[project]
    save_store(store, password)
