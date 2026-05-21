"""Tests for envault.capacity."""

import pytest

from envault.capacity import (
    set_capacity,
    get_capacity,
    remove_capacity,
    check_capacity,
    list_capacities,
)
from envault.projects import set_env
from envault.storage import save_store, load_store


PASSWORD = "test-pass"


@pytest.fixture()
def tmp_store(tmp_path):
    return tmp_path / "vault.enc"


def _seed(store_path, project="proj", keys=None):
    keys = keys or {"KEY": "val"}
    for k, v in keys.items():
        set_env(store_path, PASSWORD, project, k, v)


def test_set_and_get_capacity(tmp_store):
    _seed(tmp_store)
    set_capacity(tmp_store, PASSWORD, "proj", 10)
    assert get_capacity(tmp_store, PASSWORD, "proj") == 10


def test_get_capacity_returns_none_when_unset(tmp_store):
    _seed(tmp_store)
    assert get_capacity(tmp_store, PASSWORD, "proj") is None


def test_set_capacity_missing_project_raises(tmp_store):
    # initialise store without the target project
    _seed(tmp_store, project="other")
    with pytest.raises(KeyError, match="ghost"):
        set_capacity(tmp_store, PASSWORD, "ghost", 5)


def test_set_capacity_invalid_limit_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError):
        set_capacity(tmp_store, PASSWORD, "proj", 0)


def test_remove_capacity_returns_true(tmp_store):
    _seed(tmp_store)
    set_capacity(tmp_store, PASSWORD, "proj", 5)
    assert remove_capacity(tmp_store, PASSWORD, "proj") is True
    assert get_capacity(tmp_store, PASSWORD, "proj") is None


def test_remove_capacity_returns_false_when_not_set(tmp_store):
    _seed(tmp_store)
    assert remove_capacity(tmp_store, PASSWORD, "proj") is False


def test_check_capacity_no_limit(tmp_store):
    _seed(tmp_store, keys={"A": "1", "B": "2"})
    info = check_capacity(tmp_store, PASSWORD, "proj")
    assert info["limit"] is None
    assert info["used"] == 2
    assert info["exceeded"] is False


def test_check_capacity_not_exceeded(tmp_store):
    _seed(tmp_store, keys={"A": "1", "B": "2"})
    set_capacity(tmp_store, PASSWORD, "proj", 5)
    info = check_capacity(tmp_store, PASSWORD, "proj")
    assert info["limit"] == 5
    assert info["used"] == 2
    assert info["available"] == 3
    assert info["exceeded"] is False


def test_check_capacity_exceeded(tmp_store):
    _seed(tmp_store, keys={"A": "1", "B": "2", "C": "3"})
    set_capacity(tmp_store, PASSWORD, "proj", 2)
    info = check_capacity(tmp_store, PASSWORD, "proj")
    assert info["exceeded"] is True
    assert info["available"] == 0


def test_list_capacities_sorted(tmp_store):
    for p in ("beta", "alpha", "gamma"):
        _seed(tmp_store, project=p)
        set_capacity(tmp_store, PASSWORD, p, 10)
    entries = list_capacities(tmp_store, PASSWORD)
    assert [e["project"] for e in entries] == ["alpha", "beta", "gamma"]


def test_list_capacities_empty(tmp_store):
    _seed(tmp_store)
    assert list_capacities(tmp_store, PASSWORD) == []
