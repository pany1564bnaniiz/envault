"""Clone environment variables from one project to another."""

from __future__ import annotations

from envault.storage import load_store, save_store
from envault.projects import get_all_env, set_env


def clone_project(
    store_path,
    password: str,
    src_project: str,
    dst_project: str,
    overwrite: bool = False,
) -> int:
    """Copy all env vars from *src_project* into *dst_project*.

    Returns the number of keys copied.
    Raises KeyError if *src_project* does not exist.
    Raises ValueError if *dst_project* already exists and *overwrite* is False.
    """
    store = load_store(store_path, password)

    if src_project not in store:
        raise KeyError(f"Source project '{src_project}' not found.")

    if dst_project in store and not overwrite:
        raise ValueError(
            f"Destination project '{dst_project}' already exists. "
            "Use overwrite=True to replace it."
        )

    src_env = get_all_env(store_path, password, src_project)

    for key, value in src_env.items():
        set_env(store_path, password, dst_project, key, value)

    return len(src_env)
