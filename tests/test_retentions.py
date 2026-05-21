"""Tests for envault.retentions."""

from __future__ import annotations

import pytest

from envault.retentions import (
    delete_retention,
    expired_projects,
    get_retention,
    list_retentions,
    set_retention,
)
from envault.storage import save_store

PASSWORD = "test-secret"


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.enc")


def _seed(tmp_store: str, *projects: str) -> None:
    """Create bare project entries so retention checks can find them."""
    from envault.storage import load_store

    try:
        store = load_store(tmp_store, PASSWORD)
    except FileNotFoundError:
        store = {}
    for p in projects:
        store.setdefault(p, {})
    save_store(tmp_store, PASSWORD, store)


# ---------------------------------------------------------------------------
# set / get
# ---------------------------------------------------------------------------

def test_set_retention_returns_entry(tmp_store):
    _seed(tmp_store, "alpha")
    entry = set_retention(tmp_store, PASSWORD, "alpha", 30)
    assert entry["days"] == 30
    assert "expires_at" in entry


def test_get_retention_returns_none_when_unset(tmp_store):
    _seed(tmp_store, "alpha")
    assert get_retention(tmp_store, PASSWORD, "alpha") is None


def test_get_retention_returns_entry_after_set(tmp_store):
    _seed(tmp_store, "alpha")
    set_retention(tmp_store, PASSWORD, "alpha", 7)
    entry = get_retention(tmp_store, PASSWORD, "alpha")
    assert entry is not None
    assert entry["days"] == 7


def test_set_retention_missing_project_raises(tmp_store):
    _seed(tmp_store, "alpha")  # only alpha exists
    with pytest.raises(KeyError, match="ghost"):
        set_retention(tmp_store, PASSWORD, "ghost", 10)


def test_set_retention_invalid_days_raises(tmp_store):
    _seed(tmp_store, "alpha")
    with pytest.raises(ValueError):
        set_retention(tmp_store, PASSWORD, "alpha", 0)
    with pytest.raises(ValueError):
        set_retention(tmp_store, PASSWORD, "alpha", -5)


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

def test_delete_retention_returns_true_when_existed(tmp_store):
    _seed(tmp_store, "alpha")
    set_retention(tmp_store, PASSWORD, "alpha", 14)
    assert delete_retention(tmp_store, PASSWORD, "alpha") is True


def test_delete_retention_returns_false_when_not_set(tmp_store):
    _seed(tmp_store, "alpha")
    assert delete_retention(tmp_store, PASSWORD, "alpha") is False


def test_delete_retention_removes_entry(tmp_store):
    _seed(tmp_store, "alpha")
    set_retention(tmp_store, PASSWORD, "alpha", 14)
    delete_retention(tmp_store, PASSWORD, "alpha")
    assert get_retention(tmp_store, PASSWORD, "alpha") is None


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def test_list_retentions_empty_when_none(tmp_store):
    _seed(tmp_store, "alpha")
    assert list_retentions(tmp_store, PASSWORD) == []


def test_list_retentions_sorted_by_expiry(tmp_store):
    _seed(tmp_store, "alpha", "beta", "gamma")
    set_retention(tmp_store, PASSWORD, "gamma", 90)
    set_retention(tmp_store, PASSWORD, "alpha", 7)
    set_retention(tmp_store, PASSWORD, "beta", 30)
    result = list_retentions(tmp_store, PASSWORD)
    names = [r["project"] for r in result]
    assert names == ["alpha", "beta", "gamma"]


# ---------------------------------------------------------------------------
# expired
# ---------------------------------------------------------------------------

def test_expired_projects_none_when_all_future(tmp_store):
    _seed(tmp_store, "alpha")
    set_retention(tmp_store, PASSWORD, "alpha", 365)
    assert expired_projects(tmp_store, PASSWORD) == []


def test_expired_projects_detects_past_expiry(tmp_store):
    """Manually inject an already-expired entry."""
    from envault.storage import load_store

    _seed(tmp_store, "alpha")
    store = load_store(tmp_store, PASSWORD)
    store.setdefault("__retentions__", {})["alpha"] = {
        "days": 1,
        "expires_at": "2000-01-01T00:00:00+00:00",
    }
    save_store(tmp_store, PASSWORD, store)
    assert "alpha" in expired_projects(tmp_store, PASSWORD)
