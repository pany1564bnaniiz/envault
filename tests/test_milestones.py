"""Tests for envault.milestones."""

from __future__ import annotations

import pytest

from envault.milestones import (
    delete_milestone,
    get_milestone,
    list_milestones,
    overdue_milestones,
    set_milestone,
)
from envault.projects import set_env
from envault.storage import save_store


PASSWORD = "test-pass"


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.enc")


def _seed(store_path: str, project: str = "alpha") -> None:
    set_env(store_path, PASSWORD, project, "KEY", "val")


# ---------------------------------------------------------------------------
# set / get
# ---------------------------------------------------------------------------

def test_set_and_get_milestone(tmp_store):
    _seed(tmp_store)
    entry = set_milestone(tmp_store, PASSWORD, "alpha", "v1.0", "2030-06-01")
    assert entry["name"] == "v1.0"
    assert entry["due"] == "2030-06-01"

    fetched = get_milestone(tmp_store, PASSWORD, "alpha", "v1.0")
    assert fetched == entry


def test_get_milestone_returns_none_when_unset(tmp_store):
    _seed(tmp_store)
    assert get_milestone(tmp_store, PASSWORD, "alpha", "nonexistent") is None


def test_set_milestone_with_description(tmp_store):
    _seed(tmp_store)
    set_milestone(tmp_store, PASSWORD, "alpha", "beta", "2030-01-15", description="Beta launch")
    m = get_milestone(tmp_store, PASSWORD, "alpha", "beta")
    assert m["description"] == "Beta launch"


def test_set_milestone_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        set_milestone(tmp_store, PASSWORD, "ghost", "v1", "2030-01-01")


def test_set_milestone_invalid_date_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="Invalid ISO date"):
        set_milestone(tmp_store, PASSWORD, "alpha", "bad", "not-a-date")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def test_list_milestones_sorted_by_due(tmp_store):
    _seed(tmp_store)
    set_milestone(tmp_store, PASSWORD, "alpha", "v3", "2030-12-01")
    set_milestone(tmp_store, PASSWORD, "alpha", "v1", "2030-01-01")
    set_milestone(tmp_store, PASSWORD, "alpha", "v2", "2030-06-01")
    names = [m["name"] for m in list_milestones(tmp_store, PASSWORD, "alpha")]
    assert names == ["v1", "v2", "v3"]


def test_list_milestones_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert list_milestones(tmp_store, PASSWORD, "alpha") == []


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

def test_delete_milestone_returns_true(tmp_store):
    _seed(tmp_store)
    set_milestone(tmp_store, PASSWORD, "alpha", "v1", "2030-01-01")
    assert delete_milestone(tmp_store, PASSWORD, "alpha", "v1") is True
    assert get_milestone(tmp_store, PASSWORD, "alpha", "v1") is None


def test_delete_milestone_returns_false_when_missing(tmp_store):
    _seed(tmp_store)
    assert delete_milestone(tmp_store, PASSWORD, "alpha", "ghost") is False


# ---------------------------------------------------------------------------
# overdue
# ---------------------------------------------------------------------------

def test_overdue_milestones_returns_past_entries(tmp_store):
    _seed(tmp_store)
    set_milestone(tmp_store, PASSWORD, "alpha", "old", "2000-01-01")
    set_milestone(tmp_store, PASSWORD, "alpha", "future", "2099-01-01")
    overdue = overdue_milestones(tmp_store, PASSWORD, "alpha")
    assert len(overdue) == 1
    assert overdue[0]["name"] == "old"


def test_overdue_milestones_with_custom_as_of(tmp_store):
    _seed(tmp_store)
    set_milestone(tmp_store, PASSWORD, "alpha", "m1", "2025-03-01")
    set_milestone(tmp_store, PASSWORD, "alpha", "m2", "2025-07-01")
    overdue = overdue_milestones(tmp_store, PASSWORD, "alpha", as_of="2025-05-01")
    assert len(overdue) == 1
    assert overdue[0]["name"] == "m1"
