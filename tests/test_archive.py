"""Tests for envault.archive."""

from __future__ import annotations

import pytest

from envault.archive import (
    archive_project,
    list_archived,
    purge_archived,
    restore_project,
)
from envault.projects import get_all_env, set_env
from envault.storage import list_projects, save_store, load_store


PASSWORD = "test-pass"


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.enc")


def _seed(store_path: str, project: str = "myapp") -> None:
    set_env(store_path, PASSWORD, project, "KEY", "value")


# ---------------------------------------------------------------------------
# archive_project
# ---------------------------------------------------------------------------

def test_archive_removes_from_active(tmp_store):
    _seed(tmp_store)
    archive_project(tmp_store, PASSWORD, "myapp")
    assert "myapp" not in list_projects(tmp_store, PASSWORD)


def test_archive_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="not found"):
        archive_project(tmp_store, PASSWORD, "ghost")


def test_archive_already_archived_raises(tmp_store):
    _seed(tmp_store)
    archive_project(tmp_store, PASSWORD, "myapp")
    with pytest.raises(KeyError, match="already archived"):
        archive_project(tmp_store, PASSWORD, "myapp")


def test_archive_preserves_env_data(tmp_store):
    _seed(tmp_store)
    archive_project(tmp_store, PASSWORD, "myapp")
    store = load_store(tmp_store, PASSWORD)
    archived_env = store["__archive__"]["myapp"]["env"]
    assert archived_env.get("KEY") == "value"


# ---------------------------------------------------------------------------
# list_archived
# ---------------------------------------------------------------------------

def test_list_archived_empty_when_none(tmp_store):
    assert list_archived(tmp_store, PASSWORD) == []


def test_list_archived_returns_metadata(tmp_store):
    _seed(tmp_store)
    archive_project(tmp_store, PASSWORD, "myapp")
    entries = list_archived(tmp_store, PASSWORD)
    assert len(entries) == 1
    assert entries[0]["project"] == "myapp"
    assert "archived_at" in entries[0]


# ---------------------------------------------------------------------------
# restore_project
# ---------------------------------------------------------------------------

def test_restore_brings_project_back(tmp_store):
    _seed(tmp_store)
    archive_project(tmp_store, PASSWORD, "myapp")
    restore_project(tmp_store, PASSWORD, "myapp")
    assert "myapp" in list_projects(tmp_store, PASSWORD)


def test_restore_data_intact(tmp_store):
    _seed(tmp_store)
    archive_project(tmp_store, PASSWORD, "myapp")
    restore_project(tmp_store, PASSWORD, "myapp")
    assert get_all_env(tmp_store, PASSWORD, "myapp")["KEY"] == "value"


def test_restore_clears_archive_namespace_when_empty(tmp_store):
    _seed(tmp_store)
    archive_project(tmp_store, PASSWORD, "myapp")
    restore_project(tmp_store, PASSWORD, "myapp")
    store = load_store(tmp_store, PASSWORD)
    assert "__archive__" not in store


def test_restore_missing_raises(tmp_store):
    with pytest.raises(KeyError, match="not archived"):
        restore_project(tmp_store, PASSWORD, "ghost")


# ---------------------------------------------------------------------------
# purge_archived
# ---------------------------------------------------------------------------

def test_purge_removes_from_archive(tmp_store):
    _seed(tmp_store)
    archive_project(tmp_store, PASSWORD, "myapp")
    purge_archived(tmp_store, PASSWORD, "myapp")
    assert list_archived(tmp_store, PASSWORD) == []


def test_purge_missing_raises(tmp_store):
    with pytest.raises(KeyError, match="not archived"):
        purge_archived(tmp_store, PASSWORD, "ghost")
