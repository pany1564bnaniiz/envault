"""Tag management for envault projects.

Allows users to assign arbitrary string tags to projects for grouping
and filtering (e.g. 'production', 'staging', 'team-backend').
"""

from __future__ import annotations

from envault.storage import load_store, save_store

_TAGS_KEY = "__tags__"


def _tags_for(store: dict, project: str) -> list[str]:
    """Return the mutable tag list for *project* inside *store*."""
    project_data = store.setdefault(project, {})
    return project_data.setdefault(_TAGS_KEY, [])


def add_tag(store_path: str, password: str, project: str, tag: str) -> None:
    """Add *tag* to *project*.  No-op if the tag already exists."""
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    tags = _tags_for(store, project)
    if tag not in tags:
        tags.append(tag)
    save_store(store_path, password, store)


def remove_tag(store_path: str, password: str, project: str, tag: str) -> None:
    """Remove *tag* from *project*.  Raises KeyError if tag is absent."""
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    tags = _tags_for(store, project)
    if tag not in tags:
        raise KeyError(f"Tag '{tag}' not found on project '{project}'.")
    tags.remove(tag)
    save_store(store_path, password, store)


def list_tags(store_path: str, password: str, project: str) -> list[str]:
    """Return sorted list of tags for *project*."""
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")
    return sorted(_tags_for(store, project))


def projects_by_tag(store_path: str, password: str, tag: str) -> list[str]:
    """Return sorted list of project names that carry *tag*."""
    store = load_store(store_path, password)
    return sorted(
        name
        for name, data in store.items()
        if isinstance(data, dict) and tag in data.get(_TAGS_KEY, [])
    )
