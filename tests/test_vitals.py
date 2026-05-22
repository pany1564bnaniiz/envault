"""Tests for envault.vitals."""
import time
import pytest

from envault.projects import set_env
from envault.vitals import record_vitals, get_vitals, delete_vitals, list_vitals


PASSWORD = "vitals-pw"


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "store.enc")


def _seed(store_path, project="alpha", keys=None):
    keys = keys or {"KEY1": "v1", "KEY2": "v2"}
    for k, v in keys.items():
        set_env(store_path, PASSWORD, project, k, v)


# ---------------------------------------------------------------------------
# record_vitals
# ---------------------------------------------------------------------------

def test_record_vitals_returns_entry(tmp_store):
    _seed(tmp_store)
    entry = record_vitals(tmp_store, PASSWORD, "alpha")
    assert entry["project"] == "alpha"
    assert entry["key_count"] == 2


def test_record_vitals_persists(tmp_store):
    _seed(tmp_store)
    record_vitals(tmp_store, PASSWORD, "alpha")
    entry = get_vitals(tmp_store, PASSWORD, "alpha")
    assert entry is not None
    assert entry["key_count"] == 2


def test_record_vitals_has_timestamp(tmp_store):
    _seed(tmp_store)
    before = time.time()
    entry = record_vitals(tmp_store, PASSWORD, "alpha")
    after = time.time()
    assert before <= entry["recorded_at"] <= after


def test_record_vitals_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        record_vitals(tmp_store, PASSWORD, "ghost")


def test_record_vitals_updates_on_second_call(tmp_store):
    _seed(tmp_store, keys={"A": "1"})
    record_vitals(tmp_store, PASSWORD, "alpha")
    # Add another key and re-record.
    set_env(tmp_store, PASSWORD, "alpha", "B", "2")
    entry = record_vitals(tmp_store, PASSWORD, "alpha")
    assert entry["key_count"] == 2


# ---------------------------------------------------------------------------
# get_vitals
# ---------------------------------------------------------------------------

def test_get_vitals_returns_none_when_not_recorded(tmp_store):
    _seed(tmp_store)
    assert get_vitals(tmp_store, PASSWORD, "alpha") is None


# ---------------------------------------------------------------------------
# delete_vitals
# ---------------------------------------------------------------------------

def test_delete_vitals_returns_true_when_exists(tmp_store):
    _seed(tmp_store)
    record_vitals(tmp_store, PASSWORD, "alpha")
    assert delete_vitals(tmp_store, PASSWORD, "alpha") is True


def test_delete_vitals_returns_false_when_missing(tmp_store):
    assert delete_vitals(tmp_store, PASSWORD, "nonexistent") is False


def test_delete_vitals_removes_entry(tmp_store):
    _seed(tmp_store)
    record_vitals(tmp_store, PASSWORD, "alpha")
    delete_vitals(tmp_store, PASSWORD, "alpha")
    assert get_vitals(tmp_store, PASSWORD, "alpha") is None


# ---------------------------------------------------------------------------
# list_vitals
# ---------------------------------------------------------------------------

def test_list_vitals_empty_when_none_recorded(tmp_store):
    assert list_vitals(tmp_store, PASSWORD) == []


def test_list_vitals_sorted_by_project(tmp_store):
    for proj in ("beta", "alpha", "gamma"):
        _seed(tmp_store, project=proj, keys={"X": "1"})
        record_vitals(tmp_store, PASSWORD, proj)
    names = [e["project"] for e in list_vitals(tmp_store, PASSWORD)]
    assert names == sorted(names)


def test_list_vitals_includes_all_recorded(tmp_store):
    for proj in ("p1", "p2"):
        _seed(tmp_store, project=proj, keys={"K": "v"})
        record_vitals(tmp_store, PASSWORD, proj)
    assert len(list_vitals(tmp_store, PASSWORD)) == 2
