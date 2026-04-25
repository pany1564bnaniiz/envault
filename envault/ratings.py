"""Project ratings — let users score projects (1-5) with optional comments."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envault.storage import load_store, save_store

_RATINGS_KEY = "__ratings__"


def _ratings_map(store_path: str, password: str) -> dict:
    store = load_store(store_path, password)
    return store.get(_RATINGS_KEY, {})


def set_rating(
    store_path: str,
    password: str,
    project: str,
    score: int,
    comment: str = "",
) -> None:
    """Rate a project with a score between 1 and 5."""
    if score < 1 or score > 5:
        raise ValueError(f"Score must be between 1 and 5, got {score}")

    store = load_store(store_path, password)
    if project not in store or project == _RATINGS_KEY:
        raise KeyError(f"Project '{project}' does not exist")

    ratings = store.setdefault(_RATINGS_KEY, {})
    ratings[project] = {
        "score": score,
        "comment": comment,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_store(store_path, password, store)


def get_rating(store_path: str, password: str, project: str) -> Optional[dict]:
    """Return the rating dict for *project*, or None if unrated."""
    return _ratings_map(store_path, password).get(project)


def delete_rating(store_path: str, password: str, project: str) -> bool:
    """Remove a rating.  Returns True if one existed, False otherwise."""
    store = load_store(store_path, password)
    ratings = store.get(_RATINGS_KEY, {})
    if project not in ratings:
        return False
    del ratings[project]
    store[_RATINGS_KEY] = ratings
    save_store(store_path, password, store)
    return True


def list_ratings(store_path: str, password: str) -> dict[str, dict]:
    """Return all project ratings sorted by score descending."""
    ratings = _ratings_map(store_path, password)
    return dict(sorted(ratings.items(), key=lambda kv: kv[1]["score"], reverse=True))


def average_score(store_path: str, password: str) -> Optional[float]:
    """Return the mean score across all rated projects, or None if none exist."""
    ratings = _ratings_map(store_path, password)
    if not ratings:
        return None
    return sum(v["score"] for v in ratings.values()) / len(ratings)
