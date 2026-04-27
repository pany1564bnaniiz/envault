"""Emoji reactions for projects — lightweight sentiment/status tagging."""
from __future__ import annotations

from typing import Dict, List

from envault.storage import load_store, save_store

_REACTIONS_KEY = "__reactions__"
_VALID_REACTIONS = {"👍", "👎", "❤️", "🔥", "⚠️", "✅", "❌", "🚀", "🐛", "💡"}


def _reactions_map(store: dict) -> dict:
    return store.setdefault(_REACTIONS_KEY, {})


def add_reaction(store_path: str, password: str, project: str, emoji: str, actor: str = "user") -> None:
    """Add an emoji reaction from *actor* to *project*."""
    if emoji not in _VALID_REACTIONS:
        raise ValueError(f"Invalid reaction '{emoji}'. Valid: {sorted(_VALID_REACTIONS)}")
    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' does not exist.")
    rmap = _reactions_map(store)
    project_reactions: Dict[str, List[str]] = rmap.setdefault(project, {})
    actors: List[str] = project_reactions.setdefault(emoji, [])
    if actor not in actors:
        actors.append(actor)
    save_store(store_path, password, store)


def remove_reaction(store_path: str, password: str, project: str, emoji: str, actor: str = "user") -> None:
    """Remove *actor*'s reaction *emoji* from *project*."""
    store = load_store(store_path, password)
    rmap = _reactions_map(store)
    actors = rmap.get(project, {}).get(emoji, [])
    if actor in actors:
        actors.remove(actor)
    save_store(store_path, password, store)


def list_reactions(store_path: str, password: str, project: str) -> Dict[str, List[str]]:
    """Return a mapping of emoji -> list of actors for *project*."""
    store = load_store(store_path, password)
    rmap = _reactions_map(store)
    return {k: list(v) for k, v in rmap.get(project, {}).items() if v}


def reaction_summary(store_path: str, password: str, project: str) -> Dict[str, int]:
    """Return emoji -> count for *project*."""
    reactions = list_reactions(store_path, password, project)
    return {emoji: len(actors) for emoji, actors in reactions.items()}


def projects_reacted_by(store_path: str, password: str, actor: str) -> List[str]:
    """Return all project names that *actor* has reacted to."""
    store = load_store(store_path, password)
    rmap = _reactions_map(store)
    result = []
    for project, emojis in rmap.items():
        for actors in emojis.values():
            if actor in actors:
                result.append(project)
                break
    return sorted(result)
