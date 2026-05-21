"""Tests for envault.sprints."""
import pytest

from envault.sprints import (
    active_sprints,
    delete_sprint,
    get_sprint,
    list_sprints,
    set_sprint,
)
from envault.storage import save_store

PASS = "testpass"


@pytest.fixture()
def tmp_store(tmp_path):
    path = tmp_path / "vault.enc"
    save_store(path, PASS, {"myproject": {"KEY": "val"}})
    return path


def _seed(tmp_store):
    set_sprint(tmp_store, PASS, "myproject", "Sprint 1", "2024-01-01", "2024-01-14")


def test_set_and_get_sprint(tmp_store):
    entry = set_sprint(tmp_store, PASS, "myproject", "Sprint 1", "2024-01-01", "2024-01-14", "First sprint")
    assert entry["sprint"] == "Sprint 1"
    assert entry["start"] == "2024-01-01"
    assert entry["end"] == "2024-01-14"
    assert entry["description"] == "First sprint"

    fetched = get_sprint(tmp_store, PASS, "myproject")
    assert fetched == entry


def test_get_sprint_returns_none_when_unset(tmp_store):
    assert get_sprint(tmp_store, PASS, "myproject") is None


def test_set_sprint_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        set_sprint(tmp_store, PASS, "ghost", "S1", "2024-01-01", "2024-01-07")


def test_set_sprint_invalid_start_date_raises(tmp_store):
    with pytest.raises(ValueError, match="start_date"):
        set_sprint(tmp_store, PASS, "myproject", "S1", "not-a-date", "2024-01-07")


def test_set_sprint_invalid_end_date_raises(tmp_store):
    with pytest.raises(ValueError, match="end_date"):
        set_sprint(tmp_store, PASS, "myproject", "S1", "2024-01-01", "bad")


def test_set_sprint_end_before_start_raises(tmp_store):
    with pytest.raises(ValueError, match="end_date"):
        set_sprint(tmp_store, PASS, "myproject", "S1", "2024-01-10", "2024-01-01")


def test_delete_sprint_returns_true(tmp_store):
    _seed(tmp_store)
    assert delete_sprint(tmp_store, PASS, "myproject") is True
    assert get_sprint(tmp_store, PASS, "myproject") is None


def test_delete_sprint_returns_false_when_absent(tmp_store):
    assert delete_sprint(tmp_store, PASS, "myproject") is False


def test_list_sprints_empty(tmp_store):
    assert list_sprints(tmp_store, PASS) == {}


def test_list_sprints_returns_all(tmp_store):
    _seed(tmp_store)
    result = list_sprints(tmp_store, PASS)
    assert "myproject" in result
    assert result["myproject"]["sprint"] == "Sprint 1"


def test_active_sprints_includes_current(tmp_store):
    set_sprint(tmp_store, PASS, "myproject", "S1", "2024-01-01", "2024-12-31")
    active = active_sprints(tmp_store, PASS, as_of="2024-06-15")
    assert "myproject" in active


def test_active_sprints_excludes_future(tmp_store):
    set_sprint(tmp_store, PASS, "myproject", "S1", "2025-06-01", "2025-06-14")
    active = active_sprints(tmp_store, PASS, as_of="2024-01-01")
    assert "myproject" not in active


def test_active_sprints_excludes_past(tmp_store):
    set_sprint(tmp_store, PASS, "myproject", "S1", "2020-01-01", "2020-01-14")
    active = active_sprints(tmp_store, PASS, as_of="2024-06-15")
    assert "myproject" not in active


def test_sprints_key_not_in_list_projects(tmp_store):
    from envault.storage import list_projects
    _seed(tmp_store)
    projects = list_projects(tmp_store, PASS)
    assert "__sprints__" not in projects
