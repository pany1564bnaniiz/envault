"""Tests for envault.stale."""

from __future__ import annotations

import time
import os
import pytest

from envault.storage import save_store
from envault.stale import (
    get_last_active,
    list_stale,
    mark_stale,
    touch_project,
)


PASSWORD = "test-secret"


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.enc")


def _seed(tmp_store, *projects):
    store = {p: {"KEY": "val"} for p in projects}
    save_store(tmp_store, PASSWORD, store)


# ---------------------------------------------------------------------------

def test_touch_records_timestamp(tmp_store):
    _seed(tmp_store, "alpha")
    before = time.time()
    ts = touch_project(tmp_store, PASSWORD, "alpha")
    after = time.time()
    assert before <= ts <= after


def test_get_last_active_returns_none_when_not_touched(tmp_store):
    _seed(tmp_store, "alpha")
    assert get_last_active(tmp_store, PASSWORD, "alpha") is None


def test_get_last_active_returns_stored_timestamp(tmp_store):
    _seed(tmp_store, "alpha")
    ts = touch_project(tmp_store, PASSWORD, "alpha")
    assert get_last_active(tmp_store, PASSWORD, "alpha") == pytest.approx(ts, abs=1)


def test_touch_missing_project_raises(tmp_store):
    _seed(tmp_store, "alpha")
    with pytest.raises(KeyError, match="ghost"):
        touch_project(tmp_store, PASSWORD, "ghost")


def test_mark_stale_removes_timestamp(tmp_store):
    _seed(tmp_store, "alpha")
    touch_project(tmp_store, PASSWORD, "alpha")
    mark_stale(tmp_store, PASSWORD, "alpha")
    assert get_last_active(tmp_store, PASSWORD, "alpha") is None


def test_mark_stale_noop_when_not_touched(tmp_store):
    _seed(tmp_store, "alpha")
    mark_stale(tmp_store, PASSWORD, "alpha")  # should not raise
    assert get_last_active(tmp_store, PASSWORD, "alpha") is None


def test_list_stale_returns_never_touched(tmp_store):
    _seed(tmp_store, "alpha", "beta")
    result = list_stale(tmp_store, PASSWORD, days=30)
    names = [e["project"] for e in result]
    assert "alpha" in names
    assert "beta" in names


def test_list_stale_excludes_recently_touched(tmp_store):
    _seed(tmp_store, "alpha", "beta")
    touch_project(tmp_store, PASSWORD, "alpha")
    result = list_stale(tmp_store, PASSWORD, days=30)
    names = [e["project"] for e in result]
    assert "alpha" not in names
    assert "beta" in names


def test_list_stale_respects_days_threshold(tmp_store):
    _seed(tmp_store, "alpha")
    touch_project(tmp_store, PASSWORD, "alpha")
    # With 0 days threshold everything is stale
    result = list_stale(tmp_store, PASSWORD, days=0)
    names = [e["project"] for e in result]
    assert "alpha" in names
