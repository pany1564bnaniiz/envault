"""Tests for envault.status module."""

import pytest

from envault.projects import set_env
from envault.status import (
    get_status,
    list_statuses,
    projects_by_status,
    remove_status,
    set_status,
)


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.enc")


PASSWORD = "testpass"


def _seed(store, project="alpha"):
    set_env(store, PASSWORD, project, "KEY", "val")


def test_set_and_get_status(tmp_store):
    _seed(tmp_store)
    entry = set_status(tmp_store, PASSWORD, "alpha", "active")
    assert entry["status"] == "active"
    fetched = get_status(tmp_store, PASSWORD, "alpha")
    assert fetched["status"] == "active"
    assert "updated_at" in fetched


def test_get_status_returns_none_when_unset(tmp_store):
    _seed(tmp_store)
    assert get_status(tmp_store, PASSWORD, "alpha") is None


def test_set_status_missing_project_raises(tmp_store):
    with pytest.raises(KeyError):
        set_status(tmp_store, PASSWORD, "ghost", "active")


def test_set_status_invalid_value_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="Invalid status"):
        set_status(tmp_store, PASSWORD, "alpha", "unknown")


def test_set_status_with_note(tmp_store):
    _seed(tmp_store)
    entry = set_status(tmp_store, PASSWORD, "alpha", "deprecated", note="legacy")
    assert entry["note"] == "legacy"
    fetched = get_status(tmp_store, PASSWORD, "alpha")
    assert fetched["note"] == "legacy"


def test_remove_status_returns_true(tmp_store):
    _seed(tmp_store)
    set_status(tmp_store, PASSWORD, "alpha", "stable")
    result = remove_status(tmp_store, PASSWORD, "alpha")
    assert result is True
    assert get_status(tmp_store, PASSWORD, "alpha") is None


def test_remove_status_not_set_returns_false(tmp_store):
    _seed(tmp_store)
    result = remove_status(tmp_store, PASSWORD, "alpha")
    assert result is False


def test_list_statuses_empty(tmp_store):
    _seed(tmp_store)
    assert list_statuses(tmp_store, PASSWORD) == {}


def test_list_statuses_multiple(tmp_store):
    for proj in ("alpha", "beta", "gamma"):
        _seed(tmp_store, proj)
    set_status(tmp_store, PASSWORD, "alpha", "active")
    set_status(tmp_store, PASSWORD, "beta", "deprecated")
    mapping = list_statuses(tmp_store, PASSWORD)
    assert set(mapping.keys()) == {"alpha", "beta"}


def test_projects_by_status(tmp_store):
    for proj in ("alpha", "beta", "gamma"):
        _seed(tmp_store, proj)
    set_status(tmp_store, PASSWORD, "alpha", "active")
    set_status(tmp_store, PASSWORD, "beta", "active")
    set_status(tmp_store, PASSWORD, "gamma", "deprecated")
    active = projects_by_status(tmp_store, PASSWORD, "active")
    assert set(active) == {"alpha", "beta"}
    deprecated = projects_by_status(tmp_store, PASSWORD, "deprecated")
    assert deprecated == ["gamma"]


def test_status_not_in_list_projects(tmp_store):
    from envault.storage import list_projects
    _seed(tmp_store)
    set_status(tmp_store, PASSWORD, "alpha", "stable")
    projects = list_projects(tmp_store, PASSWORD)
    assert "__status__" not in projects
    assert "alpha" in projects
