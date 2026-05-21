"""Project voting/upvote system for envault."""

from __future__ import annotations

from typing import Dict, List

from envault.storage import load_store, save_store

_VOTES_KEY = "__votes__"


def _votes_map(store_path: str, password: str) -> dict:
    store = load_store(store_path, password)
    return store.get(_VOTES_KEY, {})


def upvote(store_path: str, password: str, project: str, actor: str) -> int:
    """Cast an upvote for *project* by *actor*. Returns new vote count."""
    store = load_store(store_path, password)
    projects = {k for k in store if not k.startswith("__")}
    if project not in projects:
        raise KeyError(f"Project '{project}' does not exist.")
    votes: dict = store.setdefault(_VOTES_KEY, {})
    entry: dict = votes.setdefault(project, {"count": 0, "voters": []})
    if actor not in entry["voters"]:
        entry["voters"].append(actor)
        entry["count"] = len(entry["voters"])
    save_store(store_path, password, store)
    return entry["count"]


def downvote(store_path: str, password: str, project: str, actor: str) -> int:
    """Remove *actor*'s upvote from *project*. Returns new vote count."""
    store = load_store(store_path, password)
    votes: dict = store.get(_VOTES_KEY, {})
    entry = votes.get(project, {"count": 0, "voters": []})
    if actor in entry["voters"]:
        entry["voters"].remove(actor)
        entry["count"] = len(entry["voters"])
        store[_VOTES_KEY] = votes
        save_store(store_path, password, store)
    return entry["count"]


def get_votes(store_path: str, password: str, project: str) -> int:
    """Return the current vote count for *project*."""
    return _votes_map(store_path, password).get(project, {}).get("count", 0)


def get_voters(store_path: str, password: str, project: str) -> List[str]:
    """Return list of actors who have upvoted *project*."""
    return list(
        _votes_map(store_path, password).get(project, {}).get("voters", [])
    )


def top_projects(store_path: str, password: str, n: int = 5) -> List[Dict]:
    """Return up to *n* projects sorted by vote count descending."""
    votes = _votes_map(store_path, password)
    ranked = sorted(
        [
            {"project": p, "count": v.get("count", 0)}
            for p, v in votes.items()
        ],
        key=lambda x: x["count"],
        reverse=True,
    )
    return ranked[:n]
