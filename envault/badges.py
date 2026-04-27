"""Project badges — attach metadata badges (e.g. 'production', 'stable') to projects."""

from __future__ import annotations

from envault.storage import load_store, save_store

_BADGES_KEY = "__badges__"

VALID_BADGES = {"production", "staging", "development", "stable", "unstable", "deprecated", "experimental"}


def _badges_map(store: dict) -> dict:
    return store.setdefault(_BADGES_KEY, {})


def add_badge(store_path: str, password: str, project: str, badge: str) -> None:
    """Add a badge to a project. Raises ValueError for unknown badges or missing projects."""
    if badge not in VALID_BADGES:
        raise ValueError(f"Unknown badge '{badge}'. Valid badges: {sorted(VALID_BADGES)}")
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    bmap = _badges_map(store)
    current = set(bmap.get(project, []))
    current.add(badge)
    bmap[project] = sorted(current)
    save_store(store_path, password, store)


def remove_badge(store_path: str, password: str, project: str, badge: str) -> bool:
    """Remove a badge from a project. Returns True if removed, False if not present."""
    store = load_store(store_path, password)
    bmap = _badges_map(store)
    current = set(bmap.get(project, []))
    if badge not in current:
        return False
    current.discard(badge)
    bmap[project] = sorted(current)
    save_store(store_path, password, store)
    return True


def list_badges(store_path: str, password: str, project: str) -> list[str]:
    """Return all badges for a project."""
    store = load_store(store_path, password)
    bmap = _badges_map(store)
    return list(bmap.get(project, []))


def projects_with_badge(store_path: str, password: str, badge: str) -> list[str]:
    """Return all projects that have a given badge."""
    store = load_store(store_path, password)
    bmap = _badges_map(store)
    return sorted(proj for proj, badges in bmap.items() if badge in badges)


def clear_badges(store_path: str, password: str, project: str) -> int:
    """Remove all badges from a project. Returns the number of badges removed."""
    store = load_store(store_path, password)
    bmap = _badges_map(store)
    count = len(bmap.get(project, []))
    bmap.pop(project, None)
    save_store(store_path, password, store)
    return count
