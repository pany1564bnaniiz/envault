"""Tests for envault.insights."""

from __future__ import annotations

import pytest

from envault.insights import (
    compute_insights,
    save_insights_snapshot,
    get_saved_insights,
    list_insights,
)
from envault.projects import set_env
from envault.storage import save_store, load_store


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.enc")


PW = "test-password"


def _seed(store_path: str, project: str = "myapp", n: int = 3) -> None:
    for i in range(n):
        set_env(store_path, PW, project, f"KEY_{i}", f"val_{i}")


def test_compute_insights_key_count(tmp_store):
    _seed(tmp_store, n=4)
    result = compute_insights(tmp_store, PW, "myapp")
    assert result["key_count"] == 4


def test_compute_insights_health_good(tmp_store):
    _seed(tmp_store, n=2)
    result = compute_insights(tmp_store, PW, "myapp")
    assert result["health"] == "good"


def test_compute_insights_health_empty(tmp_store):
    # Create project with no keys by seeding then manually clearing.
    _seed(tmp_store, n=1)
    store = load_store(tmp_store, PW)
    store["empty_proj"] = {}
    save_store(tmp_store, PW, store)
    result = compute_insights(tmp_store, PW, "empty_proj")
    assert result["health"] == "empty"


def test_compute_insights_missing_project_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError, match="ghost"):
        compute_insights(tmp_store, PW, "ghost")


def test_compute_insights_returns_project_name(tmp_store):
    _seed(tmp_store)
    result = compute_insights(tmp_store, PW, "myapp")
    assert result["project"] == "myapp"


def test_save_insights_snapshot_persists(tmp_store):
    _seed(tmp_store)
    save_insights_snapshot(tmp_store, PW, "myapp")
    saved = get_saved_insights(tmp_store, PW, "myapp")
    assert saved is not None
    assert saved["key_count"] == 3


def test_save_insights_snapshot_has_timestamp(tmp_store):
    _seed(tmp_store)
    snap = save_insights_snapshot(tmp_store, PW, "myapp")
    assert "recorded_at" in snap
    assert "T" in snap["recorded_at"]  # ISO format


def test_get_saved_insights_returns_none_when_not_saved(tmp_store):
    _seed(tmp_store)
    assert get_saved_insights(tmp_store, PW, "myapp") is None


def test_list_insights_empty_initially(tmp_store):
    _seed(tmp_store)
    assert list_insights(tmp_store, PW) == []


def test_list_insights_shows_saved_projects(tmp_store):
    _seed(tmp_store, project="alpha")
    _seed(tmp_store, project="beta")
    save_insights_snapshot(tmp_store, PW, "alpha")
    save_insights_snapshot(tmp_store, PW, "beta")
    result = list_insights(tmp_store, PW)
    assert result == ["alpha", "beta"]
