"""Tests for envault.ttl — key TTL / expiry functionality."""

from __future__ import annotations

import time
import pytest

from envault.storage import save_store
from envault.projects import set_env, get_env
from envault.ttl import set_ttl, get_ttl, purge_expired, list_expiring

PASSWORD = "test-secret"
PROJECT = "myapp"


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "store.enc")
    save_store(path, PASSWORD, {})
    return path


def _seed(store_path: str, key: str = "API_KEY", value: str = "abc123"):
    set_env(store_path, PASSWORD, PROJECT, key, value)


# ---------------------------------------------------------------------------
# set_ttl / get_ttl
# ---------------------------------------------------------------------------

def test_set_ttl_stores_expiry(tmp_store):
    _seed(tmp_store)
    before = time.time()
    set_ttl(tmp_store, PASSWORD, PROJECT, "API_KEY", ttl_seconds=60)
    expiry = get_ttl(tmp_store, PASSWORD, PROJECT, "API_KEY")
    assert expiry is not None
    assert expiry > before + 59


def test_get_ttl_returns_none_when_not_set(tmp_store):
    _seed(tmp_store)
    assert get_ttl(tmp_store, PASSWORD, PROJECT, "API_KEY") is None


def test_set_ttl_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        set_ttl(tmp_store, PASSWORD, "ghost", "KEY", 30)


def test_set_ttl_missing_key_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError, match="MISSING"):
        set_ttl(tmp_store, PASSWORD, PROJECT, "MISSING", 30)


def test_set_ttl_overwrites_existing_expiry(tmp_store):
    """Calling set_ttl a second time should replace the previous expiry."""
    _seed(tmp_store)
    set_ttl(tmp_store, PASSWORD, PROJECT, "API_KEY", ttl_seconds=60)
    first_expiry = get_ttl(tmp_store, PASSWORD, PROJECT, "API_KEY")

    set_ttl(tmp_store, PASSWORD, PROJECT, "API_KEY", ttl_seconds=120)
    second_expiry = get_ttl(tmp_store, PASSWORD, PROJECT, "API_KEY")

    assert second_expiry is not None
    assert second_expiry > first_expiry


# ---------------------------------------------------------------------------
# purge_expired
# ---------------------------------------------------------------------------

def test_purge_expired_removes_stale_key(tmp_store):
    _seed(tmp_store, "OLD_KEY", "old")
    _seed(tmp_store, "NEW_KEY", "new")
    set_ttl(tmp_store, PASSWORD, PROJECT, "OLD_KEY", ttl_seconds=-1)  # already expired
    set_ttl(tmp_store, PASSWORD, PROJECT, "NEW_KEY", ttl_seconds=3600)

    purged = purge_expired(tmp_store, PASSWORD, PROJECT)

    assert "OLD_KEY" in purged
    assert "NEW_KEY" not in purged
    with pytest.raises(KeyError):
        get_env(tmp_store, PASSWORD, PROJECT, "OLD_KEY")
    assert get_env(tmp_store, PASSWORD, PROJECT, "NEW_KEY") == "new"


def test_purge_expired_returns_empty_when_nothing_expired(tmp_store):
    _seed(tmp_store)
    set_ttl(tmp_store, PASSWORD, PROJECT, "API_KEY", ttl_seconds=3600)
    assert purge_expired(tmp_store, PASSWORD, PROJECT) == []


def test_purge_expired_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        purge_expired(tmp_store, PASSWORD, "ghost")


# ---------------------------------------------------------------------------
# list_expiring
# ---------------------------------------------------------------------------

def test_list_expiring_shows_all_ttl_keys(tmp_store):
    _seed(tmp_store, "A", "1")
    _seed(tmp_store, "B", "2")
    _seed(tmp_store, "C", "3")
