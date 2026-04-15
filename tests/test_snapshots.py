"""Tests for envault.snapshots module."""

import pytest

from envault.projects import set_env
from envault.snapshots import (
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from envault.storage import load_store, save_store

PASSWORD = "testpass"


@pytest.fixture()
def tmp_store(tmp_path, monkeypatch):
    store_file = tmp_path / "store.enc"
    monkeypatch.setattr("envault.storage._store_path", lambda: store_file)
    monkeypatch.setattr("envault.projects._store_path", lambda: store_file)
    monkeypatch.setattr("envault.snapshots.load_store",
        lambda pw, **kw: __import__("envault.storage", fromlist=["load_store"]).load_store(pw, store_path=store_file))
    monkeypatch.setattr("envault.snapshots.save_store",
        lambda store, pw, **kw: __import__("envault.storage", fromlist=["save_store"]).save_store(store, pw, store_path=store_file))
    return store_file


def _seed(store_file, project="myapp"):
    set_env(project, "KEY", "value", PASSWORD, store_path=store_file)


def test_save_snapshot_creates_entry(tmp_store):
    _seed(tmp_store)
    save_snapshot("myapp", "v1", PASSWORD)
    names = list_snapshots("myapp", PASSWORD)
    assert "v1" in names


def test_list_snapshots_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert list_snapshots("myapp", PASSWORD) == []


def test_load_snapshot_returns_env_at_save_time(tmp_store):
    _seed(tmp_store)
    save_snapshot("myapp", "before", PASSWORD)
    set_env("myapp", "KEY", "changed", PASSWORD, store_path=tmp_store)
    snap = load_snapshot("myapp", "before", PASSWORD)
    assert snap["KEY"] == "value"


def test_load_snapshot_missing_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError, match="nope"):
        load_snapshot("myapp", "nope", PASSWORD)


def test_delete_snapshot_removes_entry(tmp_store):
    _seed(tmp_store)
    save_snapshot("myapp", "v1", PASSWORD)
    delete_snapshot("myapp", "v1", PASSWORD)
    assert list_snapshots("myapp", PASSWORD) == []


def test_delete_snapshot_missing_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError):
        delete_snapshot("myapp", "ghost", PASSWORD)


def test_save_snapshot_unknown_project_raises(tmp_store):
    with pytest.raises(KeyError, match="unknown"):
        save_snapshot("unknown", "v1", PASSWORD)
