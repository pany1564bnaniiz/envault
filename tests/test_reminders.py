"""Tests for envault.reminders."""
from __future__ import annotations

import time
import pytest

from envault.storage import save_store
from envault.reminders import (
    delete_reminder,
    due_reminders,
    get_reminder,
    list_reminders,
    set_reminder,
)


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, "pw", {"myproject": {"KEY": "val"}})
    return path


def _seed(tmp_store):
    set_reminder(tmp_store, "pw", "myproject", "rotate keys", time.time() + 3600)


def test_set_and_get_reminder(tmp_store):
    set_reminder(tmp_store, "pw", "myproject", "hello", 9999999999.0)
    entry = get_reminder(tmp_store, "pw", "myproject")
    assert entry is not None
    assert entry["message"] == "hello"
    assert entry["due"] == 9999999999.0


def test_get_reminder_returns_none_when_unset(tmp_store):
    assert get_reminder(tmp_store, "pw", "myproject") is None


def test_set_reminder_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        set_reminder(tmp_store, "pw", "ghost", "msg", time.time())


def test_delete_reminder(tmp_store):
    _seed(tmp_store)
    delete_reminder(tmp_store, "pw", "myproject")
    assert get_reminder(tmp_store, "pw", "myproject") is None


def test_delete_reminder_nonexistent_is_noop(tmp_store):
    delete_reminder(tmp_store, "pw", "myproject")  # should not raise


def test_due_reminders_returns_overdue(tmp_store):
    past = time.time() - 10
    future = time.time() + 3600
    save_store(
        tmp_store,
        "pw",
        {
            "proj_a": {"K": "v"},
            "proj_b": {"K": "v"},
            "__reminders__": {
                "proj_a": {"message": "old", "due": past},
                "proj_b": {"message": "upcoming", "due": future},
            },
        },
    )
    overdue = due_reminders(tmp_store, "pw")
    assert len(overdue) == 1
    assert overdue[0]["project"] == "proj_a"


def test_list_reminders_sorted_by_due(tmp_store):
    now = time.time()
    save_store(
        tmp_store,
        "pw",
        {
            "proj_a": {"K": "v"},
            "proj_b": {"K": "v"},
            "__reminders__": {
                "proj_a": {"message": "second", "due": now + 200},
                "proj_b": {"message": "first", "due": now + 100},
            },
        },
    )
    entries = list_reminders(tmp_store, "pw")
    assert [e["project"] for e in entries] == ["proj_b", "proj_a"]


def test_list_reminders_excludes_from_list_projects(tmp_store):
    from envault.storage import list_projects
    _seed(tmp_store)
    projects = list_projects(tmp_store, "pw")
    assert "__reminders__" not in projects
