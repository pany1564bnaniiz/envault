"""Tests for envault.bookmarks."""

from __future__ import annotations

import pytest

from envault.bookmarks import (
    add_bookmark,
    get_bookmark,
    list_bookmarks,
    remove_bookmark,
    resolve_bookmark,
)
from envault.projects import set_env
from envault.storage import save_store

PASSWORD = "test-pass"


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, PASSWORD, {})
    return path


def _seed(store_path, project="myapp", key="DB_URL", value="postgres://localhost"):
    set_env(store_path, PASSWORD, project, key, value)


# ---------------------------------------------------------------------------

def test_add_bookmark_persists(tmp_store):
    _seed(tmp_store)
    add_bookmark(tmp_store, PASSWORD, "db", "myapp", "DB_URL")
    entry = get_bookmark(tmp_store, PASSWORD, "db")
    assert entry["project"] == "myapp"
    assert entry["key"] == "DB_URL"


def test_add_bookmark_with_description(tmp_store):
    _seed(tmp_store)
    add_bookmark(tmp_store, PASSWORD, "db", "myapp", "DB_URL", description="main db")
    entry = get_bookmark(tmp_store, PASSWORD, "db")
    assert entry["description"] == "main db"


def test_add_bookmark_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        add_bookmark(tmp_store, PASSWORD, "x", "ghost", "KEY")


def test_remove_bookmark(tmp_store):
    _seed(tmp_store)
    add_bookmark(tmp_store, PASSWORD, "db", "myapp", "DB_URL")
    remove_bookmark(tmp_store, PASSWORD, "db")
    with pytest.raises(KeyError):
        get_bookmark(tmp_store, PASSWORD, "db")


def test_remove_bookmark_missing_raises(tmp_store):
    with pytest.raises(KeyError, match="nope"):
        remove_bookmark(tmp_store, PASSWORD, "nope")


def test_list_bookmarks_empty(tmp_store):
    assert list_bookmarks(tmp_store, PASSWORD) == []


def test_list_bookmarks_sorted(tmp_store):
    _seed(tmp_store, project="alpha", key="K1", value="v1")
    _seed(tmp_store, project="alpha", key="K2", value="v2")
    add_bookmark(tmp_store, PASSWORD, "z-mark", "alpha", "K1")
    add_bookmark(tmp_store, PASSWORD, "a-mark", "alpha", "K2")
    names = [b["name"] for b in list_bookmarks(tmp_store, PASSWORD)]
    assert names == ["a-mark", "z-mark"]


def test_resolve_bookmark_returns_value(tmp_store):
    _seed(tmp_store, value="postgres://localhost")
    add_bookmark(tmp_store, PASSWORD, "db", "myapp", "DB_URL")
    assert resolve_bookmark(tmp_store, PASSWORD, "db") == "postgres://localhost"


def test_resolve_bookmark_missing_key_returns_none(tmp_store):
    _seed(tmp_store)
    add_bookmark(tmp_store, PASSWORD, "ghost", "myapp", "NONEXISTENT")
    assert resolve_bookmark(tmp_store, PASSWORD, "ghost") is None


def test_bookmarks_not_in_list_projects(tmp_store):
    from envault.storage import list_projects
    _seed(tmp_store)
    add_bookmark(tmp_store, PASSWORD, "db", "myapp", "DB_URL")
    projects = list_projects(tmp_store, PASSWORD)
    assert "__bookmarks__" not in projects
    assert "myapp" in projects
