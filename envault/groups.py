"""Project grouping — organize projects into named groups."""
from __future__ import annotations

from typing import Dict, List

from envault.storage import load_store, save_store

_GROUPS_KEY = "__groups__"


def _groups_map(store: dict) -> dict:
    return store.setdefault(_GROUPS_KEY, {})


def add_to_group(store_path, password: str, group: str, project: str) -> None:
    """Add *project* to *group*, creating the group if necessary."""
    store = load_store(store_path, password)
    projects = load_store(store_path, password)  # re-use same store
    # Verify project exists
    from envault.storage import list_projects
    if project not in list_projects(store_path, password):
        raise KeyError(f"Project '{project}' not found.")
    gmap = _groups_map(store)
    members: List[str] = gmap.setdefault(group, [])
    if project not in members:
        members.append(project)
    save_store(store_path, password, store)


def remove_from_group(store_path, password: str, group: str, project: str) -> None:
    """Remove *project* from *group*."""
    store = load_store(store_path, password)
    gmap = _groups_map(store)
    if group not in gmap:
        raise KeyError(f"Group '{group}' not found.")
    members: List[str] = gmap[group]
    if project not in members:
        raise KeyError(f"Project '{project}' is not in group '{group}'.")
    members.remove(project)
    if not members:
        del gmap[group]
    save_store(store_path, password, store)


def list_groups(store_path, password: str) -> Dict[str, List[str]]:
    """Return a mapping of group name -> list of member project names."""
    store = load_store(store_path, password)
    return dict(_groups_map(store))


def projects_in_group(store_path, password: str, group: str) -> List[str]:
    """Return the list of projects belonging to *group*."""
    store = load_store(store_path, password)
    gmap = _groups_map(store)
    if group not in gmap:
        raise KeyError(f"Group '{group}' not found.")
    return list(gmap[group])


def delete_group(store_path, password: str, group: str) -> int:
    """Delete an entire group. Returns the number of members removed."""
    store = load_store(store_path, password)
    gmap = _groups_map(store)
    if group not in gmap:
        raise KeyError(f"Group '{group}' not found.")
    count = len(gmap.pop(group))
    save_store(store_path, password, store)
    return count
