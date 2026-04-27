"""Tests for envault.annotations."""

from __future__ import annotations

import pytest

from envault.annotations import (
    set_annotation,
    get_annotation,
    delete_annotation,
    list_annotations,
)
from envault.projects import set_env
from envault.storage import save_store, load_store


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, "pw", {})
    return path


def _seed(store_path: str, project: str = "myapp") -> None:
    set_env(store_path, "pw", project, "DB_URL", "postgres://localhost/db")
    set_env(store_path, "pw", project, "SECRET", "abc123")


# ---------------------------------------------------------------------------
# set / get
# ---------------------------------------------------------------------------

def test_set_and_get_annotation(tmp_store):
    _seed(tmp_store)
    entry = set_annotation(tmp_store, "pw", "myapp", "DB_URL", "Primary database URL")
    assert entry["note"] == "Primary database URL"
    assert "updated_at" in entry

    fetched = get_annotation(tmp_store, "pw", "myapp", "DB_URL")
    assert fetched["note"] == "Primary database URL"


def test_get_annotation_returns_none_when_unset(tmp_store):
    _seed(tmp_store)
    result = get_annotation(tmp_store, "pw", "myapp", "SECRET")
    assert result is None


def test_set_annotation_missing_project_raises(tmp_store):
    with pytest.raises(Exception):
        set_annotation(tmp_store, "pw", "ghost", "KEY", "note")


def test_set_annotation_missing_key_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError, match="MISSING_KEY"):
        set_annotation(tmp_store, "pw", "myapp", "MISSING_KEY", "note")


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

def test_update_annotation_overwrites(tmp_store):
    _seed(tmp_store)
    set_annotation(tmp_store, "pw", "myapp", "DB_URL", "first")
    set_annotation(tmp_store, "pw", "myapp", "DB_URL", "second")
    fetched = get_annotation(tmp_store, "pw", "myapp", "DB_URL")
    assert fetched["note"] == "second"


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

def test_delete_annotation_returns_true(tmp_store):
    _seed(tmp_store)
    set_annotation(tmp_store, "pw", "myapp", "DB_URL", "note")
    assert delete_annotation(tmp_store, "pw", "myapp", "DB_URL") is True
    assert get_annotation(tmp_store, "pw", "myapp", "DB_URL") is None


def test_delete_annotation_returns_false_when_absent(tmp_store):
    _seed(tmp_store)
    assert delete_annotation(tmp_store, "pw", "myapp", "DB_URL") is False


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def test_list_annotations_empty(tmp_store):
    _seed(tmp_store)
    assert list_annotations(tmp_store, "pw", "myapp") == {}


def test_list_annotations_returns_all(tmp_store):
    _seed(tmp_store)
    set_annotation(tmp_store, "pw", "myapp", "DB_URL", "db note")
    set_annotation(tmp_store, "pw", "myapp", "SECRET", "secret note")
    result = list_annotations(tmp_store, "pw", "myapp")
    assert set(result.keys()) == {"DB_URL", "SECRET"}


# ---------------------------------------------------------------------------
# isolation
# ---------------------------------------------------------------------------

def test_annotations_not_visible_in_env(tmp_store):
    from envault.projects import get_all_env
    _seed(tmp_store)
    set_annotation(tmp_store, "pw", "myapp", "DB_URL", "note")
    env = get_all_env(tmp_store, "pw", "myapp")
    assert "__annotations__" not in env
