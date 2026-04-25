"""Tests for envault.watchers."""

from __future__ import annotations

import pytest

from envault.storage import save_store, load_store
from envault.projects import set_env
from envault.watchers import (
    add_watcher,
    remove_watcher,
    list_watchers,
    watched_projects,
)

PASSWORD = "test-secret"


@pytest.fixture()
def tmp_store(tmp_path):
    store_path = tmp_path / "vault.enc"
    return store_path


def _seed(store_path, project: str = "myapp") -> None:
    set_env(store_path, PASSWORD, project, "KEY", "val")


def test_add_watcher_persists(tmp_store):
    _seed(tmp_store)
    add_watcher(tmp_store, PASSWORD, "myapp", "alice@example.com")
    watchers = list_watchers(tmp_store, PASSWORD, "myapp")
    assert "alice@example.com" in watchers


def test_add_watcher_idempotent(tmp_store):
    _seed(tmp_store)
    add_watcher(tmp_store, PASSWORD, "myapp", "alice@example.com")
    add_watcher(tmp_store, PASSWORD, "myapp", "alice@example.com")
    watchers = list_watchers(tmp_store, PASSWORD, "myapp")
    assert watchers.count("alice@example.com") == 1


def test_add_watcher_missing_project_raises(tmp_store):
    save_store(tmp_store, PASSWORD, {})
    with pytest.raises(KeyError, match="ghost"):
        add_watcher(tmp_store, PASSWORD, "ghost", "bob@example.com")


def test_add_multiple_watchers(tmp_store):
    _seed(tmp_store)
    add_watcher(tmp_store, PASSWORD, "myapp", "alice@example.com")
    add_watcher(tmp_store, PASSWORD, "myapp", "bob@example.com")
    watchers = list_watchers(tmp_store, PASSWORD, "myapp")
    assert set(watchers) == {"alice@example.com", "bob@example.com"}


def test_remove_watcher_returns_true(tmp_store):
    _seed(tmp_store)
    add_watcher(tmp_store, PASSWORD, "myapp", "alice@example.com")
    result = remove_watcher(tmp_store, PASSWORD, "myapp", "alice@example.com")
    assert result is True
    assert list_watchers(tmp_store, PASSWORD, "myapp") == []


def test_remove_watcher_not_present_returns_false(tmp_store):
    _seed(tmp_store)
    result = remove_watcher(tmp_store, PASSWORD, "myapp", "nobody@example.com")
    assert result is False


def test_list_watchers_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert list_watchers(tmp_store, PASSWORD, "myapp") == []


def test_watched_projects_returns_correct_projects(tmp_store):
    _seed(tmp_store, "alpha")
    _seed(tmp_store, "beta")
    add_watcher(tmp_store, PASSWORD, "alpha", "carol@example.com")
    add_watcher(tmp_store, PASSWORD, "beta", "carol@example.com")
    add_watcher(tmp_store, PASSWORD, "alpha", "dave@example.com")
    result = watched_projects(tmp_store, PASSWORD, "carol@example.com")
    assert set(result) == {"alpha", "beta"}


def test_watched_projects_empty_when_not_watching(tmp_store):
    _seed(tmp_store)
    result = watched_projects(tmp_store, PASSWORD, "nobody@example.com")
    assert result == []
