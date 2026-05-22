"""Project insights: aggregate stats and health summary for a project."""

from __future__ import annotations

from typing import Any

from envault.storage import load_store, save_store
from envault.projects import get_all_env

_INSIGHTS_KEY = "__insights__"


def _insights_map(store_path: str, password: str) -> dict:
    store = load_store(store_path, password)
    return store.get(_INSIGHTS_KEY, {})


def compute_insights(store_path: str, password: str, project: str) -> dict[str, Any]:
    """Return a health/stats snapshot for *project*."""
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found.")

    env = get_all_env(store_path, password, project)
    key_count = len(env)

    # Collect optional metadata counts from known internal keys.
    meta_modules = [
        "__tags__", "__notes__", "__snapshots__", "__history__",
        "__annotations__", "__comments__", "__labels__",
    ]
    meta_present: list[str] = []
    raw_project = store.get(project, {})
    for mk in meta_modules:
        if mk in raw_project:
            meta_present.append(mk.strip("_"))

    has_ttl = "__ttl__" in store.get("__ttl__", {})
    has_quota = project in store.get("__quota__", {})

    health = "good"
    if key_count == 0:
        health = "empty"
    elif key_count > 50:
        health = "large"

    return {
        "project": project,
        "key_count": key_count,
        "metadata_modules": meta_present,
        "has_ttl": has_ttl,
        "has_quota": has_quota,
        "health": health,
    }


def save_insights_snapshot(
    store_path: str, password: str, project: str
) -> dict[str, Any]:
    """Compute and persist an insights snapshot for *project*."""
    snapshot = compute_insights(store_path, password, project)

    from datetime import datetime, timezone

    snapshot["recorded_at"] = datetime.now(timezone.utc).isoformat()

    store = load_store(store_path, password)
    insights = store.setdefault(_INSIGHTS_KEY, {})
    insights[project] = snapshot
    save_store(store_path, password, store)
    return snapshot


def get_saved_insights(store_path: str, password: str, project: str) -> dict | None:
    """Return the last persisted insights snapshot for *project*, or None."""
    return _insights_map(store_path, password).get(project)


def list_insights(store_path: str, password: str) -> list[str]:
    """Return sorted list of projects that have a saved insights snapshot."""
    return sorted(_insights_map(store_path, password).keys())
