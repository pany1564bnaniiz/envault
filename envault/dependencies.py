"""Track inter-project dependencies (one project depends on another's env vars)."""

from __future__ import annotations

from typing import List

from envault.storage import load_store, save_store

_DEPS_KEY = "__dependencies__"


def _deps_map(store: dict) -> dict:
    """Return the top-level dependencies mapping from the store."""
    return store.setdefault(_DEPS_KEY, {})


def add_dependency(store_path: str, password: str, project: str, depends_on: str) -> None:
    """Record that *project* depends on *depends_on*.

    Raises KeyError if either project does not exist.
    Raises ValueError if the dependency would create a self-loop.
    """
    if project == depends_on:
        raise ValueError(f"Project '{project}' cannot depend on itself.")

    store = load_store(store_path, password)
    projects = {k for k in store if not k.startswith("__")}
    if project not in projects:
        raise KeyError(f"Project '{project}' not found.")
    if depends_on not in projects:
        raise KeyError(f"Project '{depends_on}' not found.")

    deps = _deps_map(store)
    current = set(deps.get(project, []))
    current.add(depends_on)
    deps[project] = sorted(current)
    save_store(store_path, password, store)


def remove_dependency(store_path: str, password: str, project: str, depends_on: str) -> None:
    """Remove a dependency edge. Silently succeeds if edge did not exist."""
    store = load_store(store_path, password)
    deps = _deps_map(store)
    current = set(deps.get(project, []))
    current.discard(depends_on)
    deps[project] = sorted(current)
    save_store(store_path, password, store)


def list_dependencies(store_path: str, password: str, project: str) -> List[str]:
    """Return the list of projects that *project* directly depends on."""
    store = load_store(store_path, password)
    return list(_deps_map(store).get(project, []))


def dependents_of(store_path: str, password: str, project: str) -> List[str]:
    """Return projects that directly depend on *project*."""
    store = load_store(store_path, password)
    deps = _deps_map(store)
    return sorted(p for p, edges in deps.items() if project in edges)


def all_dependencies(store_path: str, password: str) -> dict:
    """Return the full dependency mapping {project: [depends_on, ...]}."""
    store = load_store(store_path, password)
    return {k: list(v) for k, v in _deps_map(store).items() if v}
