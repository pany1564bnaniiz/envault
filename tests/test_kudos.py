"""Tests for envault.kudos."""
from __future__ import annotations

import pytest

from envault.kudos import clear_kudos, get_kudos, give_kudos, kudos_count
from envault.projects import set_env

PASSWORD = "test-secret"


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.enc")


def _seed(store_path: str) -> None:
    set_env(store_path, PASSWORD, "alpha", "KEY", "val")


# ---------------------------------------------------------------------------
# give_kudos
# ---------------------------------------------------------------------------

def test_give_kudos_returns_entry(tmp_store):
    _seed(tmp_store)
    entry = give_kudos(tmp_store, PASSWORD, "alpha", "alice")
    assert entry["actor"] == "alice"
    assert "timestamp" in entry


def test_give_kudos_with_message(tmp_store):
    _seed(tmp_store)
    entry = give_kudos(tmp_store, PASSWORD, "alpha", "bob", message="great work!")
    assert entry["message"] == "great work!"


def test_give_kudos_persists(tmp_store):
    _seed(tmp_store)
    give_kudos(tmp_store, PASSWORD, "alpha", "alice")
    entries = get_kudos(tmp_store, PASSWORD, "alpha")
    assert len(entries) == 1
    assert entries[0]["actor"] == "alice"


def test_give_kudos_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        give_kudos(tmp_store, PASSWORD, "ghost", "alice")


def test_give_multiple_kudos(tmp_store):
    _seed(tmp_store)
    give_kudos(tmp_store, PASSWORD, "alpha", "alice")
    give_kudos(tmp_store, PASSWORD, "alpha", "bob")
    give_kudos(tmp_store, PASSWORD, "alpha", "carol")
    assert kudos_count(tmp_store, PASSWORD, "alpha") == 3


# ---------------------------------------------------------------------------
# get_kudos / kudos_count
# ---------------------------------------------------------------------------

def test_get_kudos_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert get_kudos(tmp_store, PASSWORD, "alpha") == []


def test_kudos_count_zero_when_none(tmp_store):
    _seed(tmp_store)
    assert kudos_count(tmp_store, PASSWORD, "alpha") == 0


# ---------------------------------------------------------------------------
# clear_kudos
# ---------------------------------------------------------------------------

def test_clear_kudos_returns_removed_count(tmp_store):
    _seed(tmp_store)
    give_kudos(tmp_store, PASSWORD, "alpha", "alice")
    give_kudos(tmp_store, PASSWORD, "alpha", "bob")
    removed = clear_kudos(tmp_store, PASSWORD, "alpha")
    assert removed == 2


def test_clear_kudos_empties_list(tmp_store):
    _seed(tmp_store)
    give_kudos(tmp_store, PASSWORD, "alpha", "alice")
    clear_kudos(tmp_store, PASSWORD, "alpha")
    assert get_kudos(tmp_store, PASSWORD, "alpha") == []


def test_clear_kudos_idempotent(tmp_store):
    _seed(tmp_store)
    assert clear_kudos(tmp_store, PASSWORD, "alpha") == 0
