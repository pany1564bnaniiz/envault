"""Search across projects and keys in the encrypted store."""

from __future__ import annotations

from typing import List, Tuple

from envault.storage import load_store


def search_keys(
    password: str,
    pattern: str,
    *,
    project: str | None = None,
    case_sensitive: bool = False,
) -> List[Tuple[str, str]]:
    """
    Search for keys matching *pattern* across all projects (or a single
    *project* if supplied).

    Returns a list of ``(project_name, key)`` tuples for every match.
    """
    store = load_store(password)
    needle = pattern if case_sensitive else pattern.lower()

    results: List[Tuple[str, str]] = []
    projects = [project] if project else list(store.keys())

    for proj in projects:
        if proj not in store:
            continue
        for key in store[proj]:
            haystack = key if case_sensitive else key.lower()
            if needle in haystack:
                results.append((proj, key))

    return results


def search_values(
    password: str,
    pattern: str,
    *,
    project: str | None = None,
    case_sensitive: bool = False,
) -> List[Tuple[str, str, str]]:
    """
    Search for *pattern* inside **values** across all projects (or a
    single *project*).

    Returns a list of ``(project_name, key, value)`` tuples.

    .. warning::
        This exposes plaintext values in memory; use with care.
    """
    store = load_store(password)
    needle = pattern if case_sensitive else pattern.lower()

    results: List[Tuple[str, str, str]] = []
    projects = [project] if project else list(store.keys())

    for proj in projects:
        if proj not in store:
            continue
        for key, value in store[proj].items():
            haystack = value if case_sensitive else value.lower()
            if needle in haystack:
                results.append((proj, key, value))

    return results
