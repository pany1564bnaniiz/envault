"""Forecasts: predict future project activity based on historical change data."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from envault.storage import load_store, save_store

_FORECASTS_KEY = "__forecasts__"


def _forecasts_map(store_path: str, password: str) -> dict:
    store = load_store(store_path, password)
    return store.get(_FORECASTS_KEY, {})


def record_forecast(
    store_path: str,
    password: str,
    project: str,
    horizon_days: int,
    predicted_changes: int,
    confidence: float,
    notes: str = "",
) -> dict:
    """Record a forecast entry for a project."""
    if horizon_days <= 0:
        raise ValueError("horizon_days must be a positive integer")
    if not (0.0 <= confidence <= 1.0):
        raise ValueError("confidence must be between 0.0 and 1.0")
    if predicted_changes < 0:
        raise ValueError("predicted_changes must be non-negative")

    store = load_store(store_path, password)
    if project not in store:
        raise KeyError(f"Project '{project}' not found")

    forecasts = store.setdefault(_FORECASTS_KEY, {})
    entry: dict[str, Any] = {
        "project": project,
        "horizon_days": horizon_days,
        "predicted_changes": predicted_changes,
        "confidence": round(confidence, 4),
        "notes": notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    forecasts.setdefault(project, []).append(entry)
    save_store(store_path, password, store)
    return entry


def get_forecasts(store_path: str, password: str, project: str) -> list[dict]:
    """Return all forecast entries for a project, newest first."""
    fm = _forecasts_map(store_path, password)
    return list(reversed(fm.get(project, [])))


def latest_forecast(store_path: str, password: str, project: str) -> dict | None:
    """Return the most recent forecast for a project, or None."""
    entries = get_forecasts(store_path, password, project)
    return entries[0] if entries else None


def clear_forecasts(store_path: str, password: str, project: str) -> int:
    """Delete all forecasts for a project. Returns number of entries removed."""
    store = load_store(store_path, password)
    forecasts = store.get(_FORECASTS_KEY, {})
    removed = len(forecasts.pop(project, []))
    if _FORECASTS_KEY in store:
        store[_FORECASTS_KEY] = forecasts
    save_store(store_path, password, store)
    return removed
