"""Tests for envault.quota."""

from __future__ import annotations

import pytest

from envault.storage import save_store
from envault.projects import set_env
from envault.quota import (
    set_quota,
    get_quota,
    remove_quota,
    check_quota,
    enforce_quota,
)


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, "pw", {})
    return path


def _seed(tmp_store, project="myapp", keys=None):
    keys = keys or {"KEY1": "val1"}
    for k, v in keys.items():
        set_env(tmp_store, "pw", project, k, v)
    return tmp_store


# --- set_quota ---

def test_set_quota_persists(tmp_store):
    _seed(tmp_store)
    set_quota(tmp_store, "pw", "myapp", 50)
    assert get_quota(tmp_store, "pw", "myapp") == 50


def test_set_quota_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="does not exist"):
        set_quota(tmp_store, "pw", "ghost", 10)


def test_set_quota_invalid_limit_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="positive integer"):
        set_quota(tmp_store, "pw", "myapp", 0)


def test_set_quota_updates_existing(tmp_store):
    _seed(tmp_store)
    set_quota(tmp_store, "pw", "myapp", 10)
    set_quota(tmp_store, "pw", "myapp", 99)
    assert get_quota(tmp_store, "pw", "myapp") == 99


# --- get_quota ---

def test_get_quota_returns_none_when_unset(tmp_store):
    _seed(tmp_store)
    assert get_quota(tmp_store, "pw", "myapp") is None


# --- remove_quota ---

def test_remove_quota_clears_limit(tmp_store):
    _seed(tmp_store)
    set_quota(tmp_store, "pw", "myapp", 5)
    remove_quota(tmp_store, "pw", "myapp")
    assert get_quota(tmp_store, "pw", "myapp") is None


def test_remove_quota_noop_when_unset(tmp_store):
    _seed(tmp_store)
    remove_quota(tmp_store, "pw", "myapp")  # should not raise


# --- check_quota ---

def test_check_quota_no_limit(tmp_store):
    _seed(tmp_store, keys={"A": "1", "B": "2"})
    info = check_quota(tmp_store, "pw", "myapp")
    assert info["limit"] is None
    assert info["used"] == 2
    assert info["remaining"] is None
    assert info["exceeded"] is False


def test_check_quota_within_limit(tmp_store):
    _seed(tmp_store, keys={"A": "1", "B": "2"})
    set_quota(tmp_store, "pw", "myapp", 10)
    info = check_quota(tmp_store, "pw", "myapp")
    assert info["limit"] == 10
    assert info["used"] == 2
    assert info["remaining"] == 8
    assert info["exceeded"] is False


def test_check_quota_exceeded(tmp_store):
    _seed(tmp_store, keys={"A": "1", "B": "2", "C": "3"})
    set_quota(tmp_store, "pw", "myapp", 2)
    info = check_quota(tmp_store, "pw", "myapp")
    assert info["exceeded"] is True
    assert info["remaining"] == -1


# --- enforce_quota ---

def test_enforce_quota_passes_when_within_limit(tmp_store):
    _seed(tmp_store, keys={"X": "1"})
    set_quota(tmp_store, "pw", "myapp", 5)
    enforce_quota(tmp_store, "pw", "myapp")  # should not raise


def test_enforce_quota_raises_when_exceeded(tmp_store):
    _seed(tmp_store, keys={"A": "1", "B": "2", "C": "3"})
    set_quota(tmp_store, "pw", "myapp", 2)
    with pytest.raises(PermissionError, match="exceeded its quota"):
        enforce_quota(tmp_store, "pw", "myapp")
