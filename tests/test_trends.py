"""Tests for envault.trends."""
from __future__ import annotations

import os
import pytest

from envault.storage import save_store, load_store
from envault.trends import (
    clear_trend,
    get_trend,
    record_snapshot,
    summarise_trend,
)

_PASSWORD = "test-secret"


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.enc")


def _seed(store_path: str, project: str, keys: dict | None = None) -> None:
    store = {}
    try:
        store = load_store(store_path, _PASSWORD)
    except FileNotFoundError:
        pass
    store[project] = keys or {"KEY1": "val1", "KEY2": "val2"}
    save_store(store_path, _PASSWORD, store)


# ---------------------------------------------------------------------------

def test_record_snapshot_returns_entry(tmp_store):
    _seed(tmp_store, "alpha")
    entry = record_snapshot(tmp_store, _PASSWORD, "alpha")
    assert entry["project"] == "alpha"
    assert entry["key_count"] == 2
    assert "recorded_at" in entry


def test_record_snapshot_persists(tmp_store):
    _seed(tmp_store, "alpha")
    record_snapshot(tmp_store, _PASSWORD, "alpha")
    snapshots = get_trend(tmp_store, _PASSWORD, "alpha")
    assert len(snapshots) == 1


def test_record_multiple_snapshots(tmp_store):
    _seed(tmp_store, "alpha")
    record_snapshot(tmp_store, _PASSWORD, "alpha")
    record_snapshot(tmp_store, _PASSWORD, "alpha")
    record_snapshot(tmp_store, _PASSWORD, "alpha")
    assert len(get_trend(tmp_store, _PASSWORD, "alpha")) == 3


def test_record_snapshot_missing_project_raises(tmp_store):
    _seed(tmp_store, "alpha")
    with pytest.raises(KeyError):
        record_snapshot(tmp_store, _PASSWORD, "nonexistent")


def test_get_trend_empty_when_no_snapshots(tmp_store):
    _seed(tmp_store, "alpha")
    assert get_trend(tmp_store, _PASSWORD, "alpha") == []


def test_get_trend_returns_list(tmp_store):
    _seed(tmp_store, "alpha")
    record_snapshot(tmp_store, _PASSWORD, "alpha")
    result = get_trend(tmp_store, _PASSWORD, "alpha")
    assert isinstance(result, list)
    assert result[0]["key_count"] == 2


def test_clear_trend_returns_count(tmp_store):
    _seed(tmp_store, "alpha")
    record_snapshot(tmp_store, _PASSWORD, "alpha")
    record_snapshot(tmp_store, _PASSWORD, "alpha")
    removed = clear_trend(tmp_store, _PASSWORD, "alpha")
    assert removed == 2


def test_clear_trend_removes_snapshots(tmp_store):
    _seed(tmp_store, "alpha")
    record_snapshot(tmp_store, _PASSWORD, "alpha")
    clear_trend(tmp_store, _PASSWORD, "alpha")
    assert get_trend(tmp_store, _PASSWORD, "alpha") == []


def test_summarise_trend_empty(tmp_store):
    _seed(tmp_store, "alpha")
    summary = summarise_trend(tmp_store, _PASSWORD, "alpha")
    assert summary["snapshots"] == 0


def test_summarise_trend_delta(tmp_store):
    _seed(tmp_store, "alpha", {"A": "1"})
    record_snapshot(tmp_store, _PASSWORD, "alpha")
    # add a key and record again
    store = load_store(tmp_store, _PASSWORD)
    store["alpha"]["B"] = "2"
    save_store(tmp_store, _PASSWORD, store)
    record_snapshot(tmp_store, _PASSWORD, "alpha")
    summary = summarise_trend(tmp_store, _PASSWORD, "alpha")
    assert summary["delta"] == 1
    assert summary["first_count"] == 1
    assert summary["latest_count"] == 2
