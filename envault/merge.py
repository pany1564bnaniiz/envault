"""Merge env vars from one project into another."""

from __future__ import annotations

from typing import Literal

from envault.projects import get_all_env, set_env
from envault.storage import load_store, save_store

ConflictStrategy = Literal["keep", "overwrite", "skip"]


class MergeResult:
    def __init__(self) -> None:
        self.added: list[str] = []
        self.overwritten: list[str] = []
        self.skipped: list[str] = []

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"MergeResult(added={self.added}, "
            f"overwritten={self.overwritten}, skipped={self.skipped})"
        )


def merge_projects(
    store_path: str,
    password: str,
    source: str,
    destination: str,
    conflict: ConflictStrategy = "keep",
) -> MergeResult:
    """Merge all env vars from *source* into *destination*.

    Parameters
    ----------
    conflict:
        ``"keep"``      – keep the destination value on conflict (default).
        ``"overwrite"`` – overwrite the destination value with the source value.
        ``"skip"``      – alias for ``"keep"``.
    """
    if source == destination:
        raise ValueError("Source and destination projects must be different.")

    store = load_store(store_path, password)

    if source not in store:
        raise KeyError(f"Source project '{source}' not found.")
    if destination not in store:
        raise KeyError(f"Destination project '{destination}' not found.")

    src_env = get_all_env(store_path, password, source)
    dst_env = get_all_env(store_path, password, destination)

    result = MergeResult()

    for key, value in src_env.items():
        if key in dst_env:
            if conflict == "overwrite":
                set_env(store_path, password, destination, key, value)
                result.overwritten.append(key)
            else:
                result.skipped.append(key)
        else:
            set_env(store_path, password, destination, key, value)
            result.added.append(key)

    return result
