"""Tests for envault.history."""
import pytest
from pathlib import Path
from envault.storage import save_store
from envault.history import record_change, get_history, clear_history


@pytest.fixture()
def tmp_store(tmp_path: Path):
    p = str(tmp_path / "vault.enc")
    save_store(p, "pw", {})
    return p


def _seed(store_path: str) -> None:
    from envault.projects import set_env
    set_env(store_path, "pw", "proj", "KEY", "val")


def test_record_and_retrieve(tmp_store):
    _seed(tmp_store)
    record_change(tmp_store, "pw", "proj", "KEY", None, "val", "set")
    entries = get_history(tmp_store, "pw", "proj")
    assert len(entries) == 1
    assert entries[0]["key"] == "KEY"
    assert entries[0]["action"] == "set"
    assert entries[0]["new_value"] == "val"
    assert entries[0]["old_value"] is None


def test_filter_by_key(tmp_store):
    _seed(tmp_store)
    record_change(tmp_store, "pw", "proj", "KEY", None, "v1", "set")
    record_change(tmp_store, "pw", "proj", "OTHER", None, "v2", "set")
    entries = get_history(tmp_store, "pw", "proj", key="KEY")
    assert all(e["key"] == "KEY" for e in entries)
    assert len(entries) == 1


def test_multiple_entries_ordered(tmp_store):
    _seed(tmp_store)
    record_change(tmp_store, "pw", "proj", "KEY", None, "v1", "set")
    record_change(tmp_store, "pw", "proj", "KEY", "v1", "v2", "update")
    entries = get_history(tmp_store, "pw", "proj", key="KEY")
    assert len(entries) == 2
    assert entries[0]["new_value"] == "v1"
    assert entries[1]["new_value"] == "v2"


def test_clear_history(tmp_store):
    _seed(tmp_store)
    record_change(tmp_store, "pw", "proj", "KEY", None, "val", "set")
    clear_history(tmp_store, "pw", "proj")
    assert get_history(tmp_store, "pw", "proj") == []


def test_empty_history_returns_empty_list(tmp_store):
    assert get_history(tmp_store, "pw", "no_project") == []


def test_history_not_in_list_projects(tmp_store):
    _seed(tmp_store)
    record_change(tmp_store, "pw", "proj", "KEY", None, "val", "set")
    from envault.storage import list_projects
    projects = list_projects(tmp_store, "pw")
    assert all(not p.startswith("__history__") for p in projects)
