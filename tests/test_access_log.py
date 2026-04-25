"""Tests for envault.access_log."""

from __future__ import annotations

import pytest

from envault.access_log import clear_access_log, get_access_log, record_access
from envault.projects import set_env
from envault.storage import save_store, load_store

PWD = "test-password"


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, PWD, {})
    return path


def _seed(store_path):
    set_env(store_path, PWD, "myapp", "API_KEY", "secret")


# ---------------------------------------------------------------------------
# record_access
# ---------------------------------------------------------------------------

def test_record_access_creates_entry(tmp_store):
    _seed(tmp_store)
    record_access(tmp_store, PWD, "myapp", "write", key="API_KEY")
    entries = get_access_log(tmp_store, PWD, "myapp")
    assert len(entries) == 1
    assert entries[0]["action"] == "write"
    assert entries[0]["key"] == "API_KEY"


def test_record_access_default_actor(tmp_store):
    _seed(tmp_store)
    record_access(tmp_store, PWD, "myapp", "read")
    entry = get_access_log(tmp_store, PWD, "myapp")[0]
    assert entry["actor"] == "local"


def test_record_access_custom_actor(tmp_store):
    _seed(tmp_store)
    record_access(tmp_store, PWD, "myapp", "read", actor="ci-bot")
    entry = get_access_log(tmp_store, PWD, "myapp")[0]
    assert entry["actor"] == "ci-bot"


def test_record_access_invalid_action_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="Invalid action"):
        record_access(tmp_store, PWD, "myapp", "explode")


def test_record_multiple_entries_ordered(tmp_store):
    _seed(tmp_store)
    record_access(tmp_store, PWD, "myapp", "write", key="A")
    record_access(tmp_store, PWD, "myapp", "read", key="A")
    record_access(tmp_store, PWD, "myapp", "delete", key="A")
    entries = get_access_log(tmp_store, PWD, "myapp")
    assert [e["action"] for e in entries] == ["write", "read", "delete"]


# ---------------------------------------------------------------------------
# get_access_log filtering
# ---------------------------------------------------------------------------

def test_get_access_log_filter_by_action(tmp_store):
    _seed(tmp_store)
    record_access(tmp_store, PWD, "myapp", "write", key="X")
    record_access(tmp_store, PWD, "myapp", "read", key="X")
    writes = get_access_log(tmp_store, PWD, "myapp", action="write")
    assert all(e["action"] == "write" for e in writes)
    assert len(writes) == 1


def test_get_access_log_empty_for_unknown_project(tmp_store):
    entries = get_access_log(tmp_store, PWD, "ghost")
    assert entries == []


# ---------------------------------------------------------------------------
# clear_access_log
# ---------------------------------------------------------------------------

def test_clear_access_log_returns_count(tmp_store):
    _seed(tmp_store)
    record_access(tmp_store, PWD, "myapp", "read")
    record_access(tmp_store, PWD, "myapp", "write")
    removed = clear_access_log(tmp_store, PWD, "myapp")
    assert removed == 2


def test_clear_access_log_removes_entries(tmp_store):
    _seed(tmp_store)
    record_access(tmp_store, PWD, "myapp", "read")
    clear_access_log(tmp_store, PWD, "myapp")
    assert get_access_log(tmp_store, PWD, "myapp") == []


def test_clear_access_log_unknown_project_returns_zero(tmp_store):
    assert clear_access_log(tmp_store, PWD, "ghost") == 0


# ---------------------------------------------------------------------------
# isolation: access log key not visible as a project
# ---------------------------------------------------------------------------

def test_access_log_not_in_list_projects(tmp_store):
    from envault.storage import list_projects
    _seed(tmp_store)
    record_access(tmp_store, PWD, "myapp", "read")
    projects = list_projects(tmp_store, PWD)
    assert "__access_log__" not in projects
