"""Template support: save and apply named env templates across projects."""

from __future__ import annotations

from typing import Any

from envault.storage import load_store, save_store

_TEMPLATES_KEY = "__templates__"


def _templates(store: dict) -> dict:
    return store.setdefault(_TEMPLATES_KEY, {})


def save_template(store_path: str, password: str, name: str, env: dict[str, str]) -> None:
    """Save a named template containing the given key/value pairs."""
    store = load_store(store_path, password)
    _templates(store)[name] = dict(env)
    save_store(store_path, password, store)


def load_template(store_path: str, password: str, name: str) -> dict[str, str]:
    """Return the env dict for a named template."""
    store = load_store(store_path, password)
    templates = _templates(store)
    if name not in templates:
        raise KeyError(f"Template '{name}' not found.")
    return dict(templates[name])


def list_templates(store_path: str, password: str) -> list[str]:
    """Return sorted list of all saved template names."""
    store = load_store(store_path, password)
    return sorted(_templates(store).keys())


def delete_template(store_path: str, password: str, name: str) -> None:
    """Delete a named template."""
    store = load_store(store_path, password)
    templates = _templates(store)
    if name not in templates:
        raise KeyError(f"Template '{name}' not found.")
    del templates[name]
    save_store(store_path, password, store)


def apply_template(
    store_path: str,
    password: str,
    template_name: str,
    project: str,
    overwrite: bool = False,
) -> list[str]:
    """Apply a template to a project, returning list of keys written."""
    from envault.projects import set_env, get_all_env

    env = load_template(store_path, password, template_name)
    existing = {}
    try:
        existing = get_all_env(store_path, password, project)
    except KeyError:
        pass

    written: list[str] = []
    for key, value in env.items():
        if key in existing and not overwrite:
            continue
        set_env(store_path, password, project, key, value)
        written.append(key)
    return written
