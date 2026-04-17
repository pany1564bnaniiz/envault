"""Tests for envault.notes."""

from __future__ import annotations

import pytest

from envault.notes import delete_note, get_note, list_notes, set_note
from envault.projects import set_env
from envault.storage import save_store, load_store

PASSWORD = "test-pass"


@pytest.fixture()
def tmp_store(tmp_path):
    return tmp_path / "vault.enc"


def _seed(tmp_store, project="myapp"):
    set_env(tmp_store, PASSWORD, project, "KEY", "val")


def test_set_and_get_note(tmp_store):
    _seed(tmp_store)
    set_note(tmp_store, PASSWORD, "myapp", "Remember to rotate secrets")
    note = get_note(tmp_store, PASSWORD, "myapp")
    assert note is not None
    assert note["text"] == "Remember to rotate secrets"
    assert "updated_at" in note


def test_get_note_returns_none_when_unset(tmp_store):
    _seed(tmp_store)
    assert get_note(tmp_store, PASSWORD, "myapp") is None


def test_set_note_missing_project_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError, match="ghost"):
        set_note(tmp_store, PASSWORD, "ghost", "hi")


def test_overwrite_note(tmp_store):
    _seed(tmp_store)
    set_note(tmp_store, PASSWORD, "myapp", "first")
    set_note(tmp_store, PASSWORD, "myapp", "second")
    note = get_note(tmp_store, PASSWORD, "myapp")
    assert note["text"] == "second"


def test_delete_note_returns_true_when_existed(tmp_store):
    _seed(tmp_store)
    set_note(tmp_store, PASSWORD, "myapp", "to delete")
    assert delete_note(tmp_store, PASSWORD, "myapp") is True
    assert get_note(tmp_store, PASSWORD, "myapp") is None


def test_delete_note_returns_false_when_absent(tmp_store):
    _seed(tmp_store)
    assert delete_note(tmp_store, PASSWORD, "myapp") is False


def test_list_notes(tmp_store):
    _seed(tmp_store, "app1")
    _seed(tmp_store, "app2")
    set_note(tmp_store, PASSWORD, "app1", "note one")
    set_note(tmp_store, PASSWORD, "app2", "note two")
    notes = list_notes(tmp_store, PASSWORD)
    assert set(notes.keys()) == {"app1", "app2"}


def test_list_notes_empty(tmp_store):
    _seed(tmp_store)
    assert list_notes(tmp_store, PASSWORD) == {}


def test_notes_not_in_list_projects(tmp_store):
    from envault.storage import list_projects
    _seed(tmp_store)
    set_note(tmp_store, PASSWORD, "myapp", "hidden")
    assert "__notes__" not in list_projects(tmp_store, PASSWORD)
