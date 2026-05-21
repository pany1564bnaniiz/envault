"""Tests for envault.changelog."""

from __future__ import annotations

import pytest

from envault.storage import save_store
from envault.changelog import add_entry, get_changelog, clear_changelog


@pytest.fixture()
def tmp_store(tmp_path):
    return tmp_path / "vault.enc"


def _seed(tmp_store, password="pw"):
    save_store(tmp_store, password, {"myproject": {"KEY": "val"}})


def test_add_entry_returns_dict(tmp_store):
    _seed(tmp_store)
    entry = add_entry(tmp_store, "pw", "myproject", "Initial release")
    assert entry["message"] == "Initial release"
    assert "timestamp" in entry
    assert entry["author"] == "envault"


def test_add_entry_custom_author(tmp_store):
    _seed(tmp_store)
    entry = add_entry(tmp_store, "pw", "myproject", "Fix", author="alice")
    assert entry["author"] == "alice"


def test_add_entry_missing_project_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError, match="ghost"):
        add_entry(tmp_store, "pw", "ghost", "oops")


def test_get_changelog_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert get_changelog(tmp_store, "pw", "myproject") == []


def test_get_changelog_returns_entries_in_order(tmp_store):
    _seed(tmp_store)
    add_entry(tmp_store, "pw", "myproject", "first")
    add_entry(tmp_store, "pw", "myproject", "second")
    entries = get_changelog(tmp_store, "pw", "myproject")
    assert len(entries) == 2
    assert entries[0]["message"] == "first"
    assert entries[1]["message"] == "second"


def test_get_changelog_missing_project_returns_empty(tmp_store):
    _seed(tmp_store)
    assert get_changelog(tmp_store, "pw", "nonexistent") == []


def test_clear_changelog_returns_count(tmp_store):
    _seed(tmp_store)
    add_entry(tmp_store, "pw", "myproject", "a")
    add_entry(tmp_store, "pw", "myproject", "b")
    removed = clear_changelog(tmp_store, "pw", "myproject")
    assert removed == 2


def test_clear_changelog_empties_entries(tmp_store):
    _seed(tmp_store)
    add_entry(tmp_store, "pw", "myproject", "a")
    clear_changelog(tmp_store, "pw", "myproject")
    assert get_changelog(tmp_store, "pw", "myproject") == []


def test_clear_changelog_no_entries_returns_zero(tmp_store):
    _seed(tmp_store)
    assert clear_changelog(tmp_store, "pw", "myproject") == 0


def test_entries_persist_across_loads(tmp_store):
    _seed(tmp_store)
    add_entry(tmp_store, "pw", "myproject", "persisted")
    entries = get_changelog(tmp_store, "pw", "myproject")
    assert entries[0]["message"] == "persisted"
