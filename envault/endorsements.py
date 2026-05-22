"""Endorsements: let users endorse projects for specific skills or qualities."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from envault.storage import load_store, save_store

_ENDORSEMENTS_KEY = "__endorsements__"

VALID_QUALITIES = {
    "reliable", "well-documented", "secure", "minimal", "production-ready",
    "well-tested", "actively-maintained", "easy-to-use",
}


def _endorsements_map(store: dict) -> dict:
    return store.setdefault(_ENDORSEMENTS_KEY, {})


def endorse(store_path: str, password: str, project: str, quality: str, actor: str = "anonymous") -> dict[str, Any]:
    """Add an endorsement for a project quality. Idempotent per actor+quality."""
    if quality not in VALID_QUALITIES:
        raise ValueError(f"Invalid quality '{quality}'. Choose from: {sorted(VALID_QUALITIES)}")

    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' does not exist.")

    em = _endorsements_map(store)
    project_endorsements = em.setdefault(project, {})
    quality_endorsements = project_endorsements.setdefault(quality, [])

    for entry in quality_endorsements:
        if entry["actor"] == actor:
            return entry  # idempotent

    entry = {
        "actor": actor,
        "quality": quality,
        "endorsed_at": datetime.now(timezone.utc).isoformat(),
    }
    quality_endorsements.append(entry)
    save_store(store_path, password, store)
    return entry


def withdraw(store_path: str, password: str, project: str, quality: str, actor: str = "anonymous") -> bool:
    """Remove an endorsement. Returns True if removed, False if not found."""
    store = load_store(store_path, password)
    em = _endorsements_map(store)
    quality_endorsements = em.get(project, {}).get(quality, [])
    original_len = len(quality_endorsements)
    em.get(project, {}).setdefault(quality, [])
    em[project][quality] = [e for e in quality_endorsements if e["actor"] != actor]
    if len(em[project][quality]) < original_len:
        save_store(store_path, password, store)
        return True
    return False


def list_endorsements(store_path: str, password: str, project: str) -> dict[str, list[dict]]:
    """Return all endorsements for a project, grouped by quality."""
    store = load_store(store_path, password)
    em = _endorsements_map(store)
    return dict(em.get(project, {}))


def endorsement_counts(store_path: str, password: str, project: str) -> dict[str, int]:
    """Return endorsement counts per quality for a project."""
    endorsements = list_endorsements(store_path, password, project)
    return {quality: len(entries) for quality, entries in endorsements.items() if entries}
