"""Tests for envault.deadlines."""
import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from envault.deadlines import (
    delete_deadline,
    get_deadline,
    list_deadlines,
    overdue_projects,
    set_deadline,
)
from envault.storage import save_store

PASSWORD = "testpass"


@pytest.fixture()
def tmp_store(tmp_path):
    return tmp_path / "vault.enc"


def _seed(store_path, *projects):
    store = {p: {"KEY": "val"} for p in projects}
    save_store(store_path, PASSWORD, store)


def _future(days=1):
    return datetime.now(tz=timezone.utc) + timedelta(days=days)


def _past(days=1):
    return datetime.now(tz=timezone.utc) - timedelta(days=days)


def test_set_and_get_deadline(tmp_store):
    _seed(tmp_store, "alpha")
    due = _future()
    set_deadline(tmp_store, PASSWORD, "alpha", due, label="launch")
    info = get_deadline(tmp_store, PASSWORD, "alpha")
    assert info is not None
    assert info["label"] == "launch"
    assert datetime.fromisoformat(info["due"]).date() == due.date()


def test_get_deadline_returns_none_when_unset(tmp_store):
    _seed(tmp_store, "beta")
    assert get_deadline(tmp_store, PASSWORD, "beta") is None


def test_set_deadline_missing_project_raises(tmp_store):
    _seed(tmp_store, "alpha")
    with pytest.raises(KeyError, match="ghost"):
        set_deadline(tmp_store, PASSWORD, "ghost", _future())


def test_delete_deadline(tmp_store):
    _seed(tmp_store, "alpha")
    set_deadline(tmp_store, PASSWORD, "alpha", _future())
    delete_deadline(tmp_store, PASSWORD, "alpha")
    assert get_deadline(tmp_store, PASSWORD, "alpha") is None


def test_delete_deadline_not_set_raises(tmp_store):
    _seed(tmp_store, "alpha")
    with pytest.raises(KeyError):
        delete_deadline(tmp_store, PASSWORD, "alpha")


def test_list_deadlines_sorted(tmp_store):
    _seed(tmp_store, "a", "b", "c")
    set_deadline(tmp_store, PASSWORD, "c", _future(3))
    set_deadline(tmp_store, PASSWORD, "a", _future(1))
    set_deadline(tmp_store, PASSWORD, "b", _future(2))
    entries = list_deadlines(tmp_store, PASSWORD)
    assert [e["project"] for e in entries] == ["a", "b", "c"]


def test_list_deadlines_empty(tmp_store):
    _seed(tmp_store, "alpha")
    assert list_deadlines(tmp_store, PASSWORD) == []


def test_overdue_projects(tmp_store):
    _seed(tmp_store, "old", "new")
    set_deadline(tmp_store, PASSWORD, "old", _past(2))
    set_deadline(tmp_store, PASSWORD, "new", _future(2))
    overdue = overdue_projects(tmp_store, PASSWORD)
    assert len(overdue) == 1
    assert overdue[0]["project"] == "old"


def test_overdue_projects_none(tmp_store):
    _seed(tmp_store, "alpha")
    set_deadline(tmp_store, PASSWORD, "alpha", _future(10))
    assert overdue_projects(tmp_store, PASSWORD) == []
