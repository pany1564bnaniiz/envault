"""Tests for envault.subscriptions."""

from __future__ import annotations

import pytest

from envault.storage import save_store
from envault.subscriptions import (
    subscribe,
    unsubscribe,
    list_subscribers,
    subscriptions_for,
)


@pytest.fixture()
def tmp_store(tmp_path):
    return tmp_path / "vault.db"


PASSWORD = "s3cret"


def _seed(store_path, *projects):
    store = {p: {"KEY": "val"} for p in projects}
    save_store(store_path, PASSWORD, store)


def test_subscribe_persists(tmp_store):
    _seed(tmp_store, "alpha")
    subscribe(tmp_store, PASSWORD, "alpha", "alice")
    assert "alice" in list_subscribers(tmp_store, PASSWORD, "alpha")


def test_subscribe_idempotent(tmp_store):
    _seed(tmp_store, "alpha")
    subscribe(tmp_store, PASSWORD, "alpha", "alice")
    subscribe(tmp_store, PASSWORD, "alpha", "alice")
    assert list_subscribers(tmp_store, PASSWORD, "alpha").count("alice") == 1


def test_subscribe_missing_project_raises(tmp_store):
    _seed(tmp_store, "alpha")
    with pytest.raises(KeyError, match="ghost"):
        subscribe(tmp_store, PASSWORD, "ghost", "alice")


def test_unsubscribe_removes_user(tmp_store):
    _seed(tmp_store, "alpha")
    subscribe(tmp_store, PASSWORD, "alpha", "alice")
    unsubscribe(tmp_store, PASSWORD, "alpha", "alice")
    assert "alice" not in list_subscribers(tmp_store, PASSWORD, "alpha")


def test_unsubscribe_silent_when_not_subscribed(tmp_store):
    _seed(tmp_store, "alpha")
    # Should not raise
    unsubscribe(tmp_store, PASSWORD, "alpha", "nobody")


def test_list_subscribers_sorted(tmp_store):
    _seed(tmp_store, "alpha")
    for user in ("zara", "alice", "bob"):
        subscribe(tmp_store, PASSWORD, "alpha", user)
    assert list_subscribers(tmp_store, PASSWORD, "alpha") == ["alice", "bob", "zara"]


def test_list_subscribers_empty_when_none(tmp_store):
    _seed(tmp_store, "alpha")
    assert list_subscribers(tmp_store, PASSWORD, "alpha") == []


def test_subscriptions_for_user(tmp_store):
    _seed(tmp_store, "alpha", "beta", "gamma")
    subscribe(tmp_store, PASSWORD, "alpha", "alice")
    subscribe(tmp_store, PASSWORD, "gamma", "alice")
    subscribe(tmp_store, PASSWORD, "beta", "bob")
    result = subscriptions_for(tmp_store, PASSWORD, "alice")
    assert result == ["alpha", "gamma"]


def test_subscriptions_for_user_empty(tmp_store):
    _seed(tmp_store, "alpha")
    assert subscriptions_for(tmp_store, PASSWORD, "nobody") == []


def test_multiple_subscribers_same_project(tmp_store):
    _seed(tmp_store, "alpha")
    for user in ("alice", "bob", "carol"):
        subscribe(tmp_store, PASSWORD, "alpha", user)
    subs = list_subscribers(tmp_store, PASSWORD, "alpha")
    assert len(subs) == 3
    assert "carol" in subs
