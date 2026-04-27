"""Tests for envault.priorities."""

from __future__ import annotations

import pytest

from envault.priorities import (
    get_priority,
    list_priorities,
    projects_by_priority,
    remove_priority,
    set_priority,
)
from envault.storage import save_store

PASSWORD = "test-secret"


@pytest.fixture()
def tmp_store(tmp_path):
    return tmp_path / "vault.enc"


def _seed(tmp_store, *projects):
    store = {p: {"KEY": "val"} for p in projects}
    save_store(tmp_store, PASSWORD, store)


def test_set_and_get_priority(tmp_store):
    _seed(tmp_store, "alpha")
    set_priority(tmp_store, PASSWORD, "alpha", "high")
    assert get_priority(tmp_store, PASSWORD, "alpha") == "high"


def test_get_priority_returns_none_when_unset(tmp_store):
    _seed(tmp_store, "alpha")
    assert get_priority(tmp_store, PASSWORD, "alpha") is None


def test_set_priority_missing_project_raises(tmp_store):
    _seed(tmp_store, "alpha")
    with pytest.raises(KeyError, match="ghost"):
        set_priority(tmp_store, PASSWORD, "ghost", "low")


def test_set_priority_invalid_level_raises(tmp_store):
    _seed(tmp_store, "alpha")
    with pytest.raises(ValueError, match="Invalid priority"):
        set_priority(tmp_store, PASSWORD, "alpha", "urgent")


def test_remove_priority_returns_true_when_existed(tmp_store):
    _seed(tmp_store, "alpha")
    set_priority(tmp_store, PASSWORD, "alpha", "low")
    assert remove_priority(tmp_store, PASSWORD, "alpha") is True
    assert get_priority(tmp_store, PASSWORD, "alpha") is None


def test_remove_priority_returns_false_when_not_set(tmp_store):
    _seed(tmp_store, "alpha")
    assert remove_priority(tmp_store, PASSWORD, "alpha") is False


def test_list_priorities_empty_when_none_set(tmp_store):
    _seed(tmp_store, "alpha", "beta")
    assert list_priorities(tmp_store, PASSWORD) == {}


def test_list_priorities_returns_all(tmp_store):
    _seed(tmp_store, "alpha", "beta", "gamma")
    set_priority(tmp_store, PASSWORD, "alpha", "high")
    set_priority(tmp_store, PASSWORD, "beta", "low")
    result = list_priorities(tmp_store, PASSWORD)
    assert result == {"alpha": "high", "beta": "low"}


def test_projects_by_priority_filters_correctly(tmp_store):
    _seed(tmp_store, "alpha", "beta", "gamma")
    set_priority(tmp_store, PASSWORD, "alpha", "critical")
    set_priority(tmp_store, PASSWORD, "beta", "critical")
    set_priority(tmp_store, PASSWORD, "gamma", "medium")
    result = projects_by_priority(tmp_store, PASSWORD, "critical")
    assert sorted(result) == ["alpha", "beta"]


def test_projects_by_priority_invalid_level_raises(tmp_store):
    _seed(tmp_store, "alpha")
    with pytest.raises(ValueError, match="Invalid priority"):
        projects_by_priority(tmp_store, PASSWORD, "extreme")


def test_update_priority_overwrites(tmp_store):
    _seed(tmp_store, "alpha")
    set_priority(tmp_store, PASSWORD, "alpha", "low")
    set_priority(tmp_store, PASSWORD, "alpha", "critical")
    assert get_priority(tmp_store, PASSWORD, "alpha") == "critical"
