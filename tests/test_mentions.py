"""tests/test_mentions.py — tests for envault.mentions."""
from __future__ import annotations

import pytest

from envault.storage import save_store
from envault.mentions import add_mention, list_mentions, mentions_for_user, clear_mentions

PASSWORD = "test-pass"


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.db")
    save_store(path, PASSWORD, {"projects": {"alpha": {"KEY": "val"}, "beta": {"X": "1"}}})
    return path


def _seed(tmp_store):
    """Helper: seed one mention on alpha."""
    return add_mention(tmp_store, PASSWORD, "alpha", "alice", "check this")


# ---------------------------------------------------------------------------
# add_mention
# ---------------------------------------------------------------------------

def test_add_mention_returns_entry(tmp_store):
    entry = _seed(tmp_store)
    assert entry["user"] == "alice"
    assert entry["message"] == "check this"
    assert "timestamp" in entry


def test_add_mention_persists(tmp_store):
    _seed(tmp_store)
    entries = list_mentions(tmp_store, PASSWORD, "alpha")
    assert len(entries) == 1
    assert entries[0]["user"] == "alice"


def test_add_mention_multiple(tmp_store):
    add_mention(tmp_store, PASSWORD, "alpha", "alice")
    add_mention(tmp_store, PASSWORD, "alpha", "bob", "hi")
    entries = list_mentions(tmp_store, PASSWORD, "alpha")
    assert len(entries) == 2
    assert entries[1]["user"] == "bob"


def test_add_mention_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        add_mention(tmp_store, PASSWORD, "ghost", "alice")


def test_add_mention_no_message(tmp_store):
    entry = add_mention(tmp_store, PASSWORD, "alpha", "carol")
    assert entry["message"] == ""


# ---------------------------------------------------------------------------
# list_mentions
# ---------------------------------------------------------------------------

def test_list_mentions_empty(tmp_store):
    assert list_mentions(tmp_store, PASSWORD, "alpha") == []


def test_list_mentions_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        list_mentions(tmp_store, PASSWORD, "ghost")


# ---------------------------------------------------------------------------
# mentions_for_user
# ---------------------------------------------------------------------------

def test_mentions_for_user_finds_entries(tmp_store):
    add_mention(tmp_store, PASSWORD, "alpha", "alice")
    add_mention(tmp_store, PASSWORD, "beta", "alice", "urgent")
    result = mentions_for_user(tmp_store, PASSWORD, "alice")
    assert set(result.keys()) == {"alpha", "beta"}


def test_mentions_for_user_excludes_others(tmp_store):
    add_mention(tmp_store, PASSWORD, "alpha", "bob")
    result = mentions_for_user(tmp_store, PASSWORD, "alice")
    assert result == {}


def test_mentions_for_user_empty_store(tmp_store):
    assert mentions_for_user(tmp_store, PASSWORD, "nobody") == {}


# ---------------------------------------------------------------------------
# clear_mentions
# ---------------------------------------------------------------------------

def test_clear_mentions_returns_count(tmp_store):
    add_mention(tmp_store, PASSWORD, "alpha", "alice")
    add_mention(tmp_store, PASSWORD, "alpha", "bob")
    count = clear_mentions(tmp_store, PASSWORD, "alpha")
    assert count == 2


def test_clear_mentions_removes_entries(tmp_store):
    _seed(tmp_store)
    clear_mentions(tmp_store, PASSWORD, "alpha")
    assert list_mentions(tmp_store, PASSWORD, "alpha") == []


def test_clear_mentions_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        clear_mentions(tmp_store, PASSWORD, "ghost")
