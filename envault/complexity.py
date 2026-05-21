"""Project complexity scoring based on key count, nesting, and metadata richness."""

from __future__ import annotations

from typing import Any

from envault.storage import load_store, save_store

_COMPLEXITY_KEY = "__complexity_config__"

WEIGHTS = {
    "key_count": 1,
    "has_tags": 5,
    "has_notes": 3,
    "has_snapshots": 4,
    "has_history": 2,
    "has_dependencies": 6,
    "has_hooks": 4,
    "has_annotations": 2,
}


def _complexity_config(store: dict) -> dict:
    return store.setdefault(_COMPLEXITY_KEY, {})


def compute_complexity(project: str, password: str, store_path=None) -> dict[str, Any]:
    """Compute a complexity score for *project* based on its metadata."""
    store = load_store(password, path=store_path)
    if project not in store or project.startswith("__"):
        raise KeyError(f"Project '{project}' not found.")

    env = {k: v for k, v in store[project].items() if not k.startswith("__")}
    key_count = len(env)

    flags = {
        "key_count": key_count,
        "has_tags": bool(store[project].get("__tags__")),
        "has_notes": bool(store[project].get("__notes__")),
        "has_snapshots": any(
            k.startswith(f"__snapshot__{project}__") for k in store
        ),
        "has_history": bool(store[project].get("__history__")),
        "has_dependencies": bool(
            store.get("__deps__", {}).get(project)
        ),
        "has_hooks": bool(store[project].get("__hooks__")),
        "has_annotations": bool(store[project].get("__annotations__")),
    }

    score = sum(
        WEIGHTS.get(k, 1) * (v if isinstance(v, int) else int(bool(v)))
        for k, v in flags.items()
    )

    return {"project": project, "score": score, "breakdown": flags}


def rank_projects(password: str, store_path=None) -> list[dict[str, Any]]:
    """Return all projects sorted by complexity score descending."""
    store = load_store(password, path=store_path)
    projects = [
        p for p in store
        if not p.startswith("__")
    ]
    results = [
        compute_complexity(p, password, store_path=store_path)
        for p in projects
    ]
    return sorted(results, key=lambda r: r["score"], reverse=True)
