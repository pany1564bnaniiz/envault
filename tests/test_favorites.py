"""Tests for envault.favorites."""
from __future__ import annotations

import pytest

from envault.storage import save_store
from envault.projects import set_env
from envault.favorites import add_favorite, remove_favorite, list_favorites, is_favorite

PASSWORD = "pw"


@pytest.fixture
def tmp_store(tmp_path):
    path = tmp_path / "store.db"
    save_store(path, PASSWORD, {})
    return path


def _seed(tmp_store, project="myapp"):
    set_env(tmp_store, PASSWORD, project, "KEY", "val")


def test_add_favorite_persists(tmp_store):
    _seed(tmp_store)
    add_favorite(tmp_store, PASSWORD, "myapp")
    assert "myapp" in list_favorites(tmp_store, PASSWORD)


def test_add_favorite_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="not found"):
        add_favorite(tmp_store, PASSWORD, "ghost")


def test_add_favorite_idempotent(tmp_store):
    _seed(tmp_store)
    add_favorite(tmp_store, PASSWORD, "myapp")
    add_favorite(tmp_store, PASSWORD, "myapp")
    assert list_favorites(tmp_store, PASSWORD).count("myapp") == 1


def test_remove_favorite(tmp_store):
    _seed(tmp_store)
    add_favorite(tmp_store, PASSWORD, "myapp")
    remove_favorite(tmp_store, PASSWORD, "myapp")
    assert "myapp" not in list_favorites(tmp_store, PASSWORD)


def test_remove_favorite_not_set_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError, match="not a favorite"):
        remove_favorite(tmp_store, PASSWORD, "myapp")


def test_list_favorites_empty(tmp_store):
    assert list_favorites(tmp_store, PASSWORD) == []


def test_list_favorites_sorted(tmp_store):
    for name in ["zebra", "alpha", "mid"]:
        set_env(tmp_store, PASSWORD, name, "K", "v")
        add_favorite(tmp_store, PASSWORD, name)
    assert list_favorites(tmp_store, PASSWORD) == ["alpha", "mid", "zebra"]


def test_is_favorite_true(tmp_store):
    _seed(tmp_store)
    add_favorite(tmp_store, PASSWORD, "myapp")
    assert is_favorite(tmp_store, PASSWORD, "myapp") is True


def test_is_favorite_false(tmp_store):
    _seed(tmp_store)
    assert is_favorite(tmp_store, PASSWORD, "myapp") is False
