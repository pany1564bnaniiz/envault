"""Tests for envault.comments."""

from __future__ import annotations

import pytest

from envault.storage import save_store
from envault.projects import set_env
from envault.comments import (
    set_comment,
    get_comment,
    delete_comment,
    list_comments,
)


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.db")


PASSWORD = "hunter2"


def _seed(store_path: str, project: str = "web") -> None:
    set_env(store_path, PASSWORD, project, "API_KEY", "abc123")
    set_env(store_path, PASSWORD, project, "DB_URL", "postgres://localhost/db")


def test_set_and_get_comment(tmp_store):
    _seed(tmp_store)
    set_comment(tmp_store, PASSWORD, "web", "API_KEY", "Primary API key")
    assert get_comment(tmp_store, PASSWORD, "web", "API_KEY") == "Primary API key"


def test_get_comment_returns_none_when_unset(tmp_store):
    _seed(tmp_store)
    assert get_comment(tmp_store, PASSWORD, "web", "DB_URL") is None


def test_set_comment_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        set_comment(tmp_store, PASSWORD, "ghost", "KEY", "oops")


def test_set_comment_missing_key_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError, match="MISSING"):
        set_comment(tmp_store, PASSWORD, "web", "MISSING", "nope")


def test_overwrite_comment(tmp_store):
    _seed(tmp_store)
    set_comment(tmp_store, PASSWORD, "web", "API_KEY", "first")
    set_comment(tmp_store, PASSWORD, "web", "API_KEY", "second")
    assert get_comment(tmp_store, PASSWORD, "web", "API_KEY") == "second"


def test_delete_comment_returns_true(tmp_store):
    _seed(tmp_store)
    set_comment(tmp_store, PASSWORD, "web", "API_KEY", "to remove")
    assert delete_comment(tmp_store, PASSWORD, "web", "API_KEY") is True
    assert get_comment(tmp_store, PASSWORD, "web", "API_KEY") is None


def test_delete_comment_returns_false_when_absent(tmp_store):
    _seed(tmp_store)
    assert delete_comment(tmp_store, PASSWORD, "web", "API_KEY") is False


def test_list_comments_empty(tmp_store):
    _seed(tmp_store)
    assert list_comments(tmp_store, PASSWORD, "web") == {}


def test_list_comments_multiple(tmp_store):
    _seed(tmp_store)
    set_comment(tmp_store, PASSWORD, "web", "API_KEY", "the key")
    set_comment(tmp_store, PASSWORD, "web", "DB_URL", "database connection")
    result = list_comments(tmp_store, PASSWORD, "web")
    assert result == {"API_KEY": "the key", "DB_URL": "database connection"}


def test_comments_isolated_between_projects(tmp_store):
    _seed(tmp_store, "web")
    _seed(tmp_store, "worker")
    set_comment(tmp_store, PASSWORD, "web", "API_KEY", "web comment")
    assert get_comment(tmp_store, PASSWORD, "worker", "API_KEY") is None
