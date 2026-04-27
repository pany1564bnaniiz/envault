"""Project scorecards: aggregate health metrics into a single score."""

from __future__ import annotations

from typing import Any

from envault.storage import load_store, save_store

_SCORECARD_KEY = "__scorecards__"

VALID_METRICS = {"completeness", "freshness", "security", "documentation", "stability"}


def _scorecards_map(store: dict) -> dict:
    return store.setdefault(_SCORECARD_KEY, {})


def set_metric(
    store_path: str,
    password: str,
    project: str,
    metric: str,
    value: float,
) -> None:
    """Set a named metric (0.0–1.0) for a project's scorecard."""
    if metric not in VALID_METRICS:
        raise ValueError(f"Invalid metric '{metric}'. Valid: {sorted(VALID_METRICS)}")
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"Metric value must be between 0.0 and 1.0, got {value}")
    store = load_store(store_path, password)
    projects = {k for k in store if not k.startswith("__")}
    if project not in projects:
        raise KeyError(f"Project '{project}' not found")
    sc = _scorecards_map(store)
    sc.setdefault(project, {})[metric] = round(value, 4)
    save_store(store_path, password, store)


def get_scorecard(store_path: str, password: str, project: str) -> dict[str, float]:
    """Return all metrics for a project (may be empty)."""
    store = load_store(store_path, password)
    return dict(_scorecards_map(store).get(project, {}))


def overall_score(store_path: str, password: str, project: str) -> float | None:
    """Return the mean of all set metrics, or None if no metrics exist."""
    metrics = get_scorecard(store_path, password, project)
    if not metrics:
        return None
    return round(sum(metrics.values()) / len(metrics), 4)


def delete_metric(
    store_path: str, password: str, project: str, metric: str
) -> bool:
    """Remove a single metric. Returns True if it existed."""
    store = load_store(store_path, password)
    sc = _scorecards_map(store)
    removed = sc.get(project, {}).pop(metric, None) is not None
    if removed:
        save_store(store_path, password, store)
    return removed


def list_scorecards(store_path: str, password: str) -> dict[str, dict[str, float]]:
    """Return scorecards for all projects that have at least one metric."""
    store = load_store(store_path, password)
    return {k: dict(v) for k, v in _scorecards_map(store).items() if v}
