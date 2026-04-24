"""Tests for envault.groups."""
import pytest

from envault.storage import save_store, load_store
from envault.projects import set_env
from envault.groups import (
    add_to_group,
    remove_from_group,
    list_groups,
    projects_in_group,
    delete_group,
)

PASSWORD = "test-password"


@pytest.fixture()
def tmp_store(tmp_path):
    path = tmp_path / "vault.enc"
    save_store(path, PASSWORD, {})
    return path


def _seed(store_path, project, key="KEY", value="val"):
    set_env(store_path, PASSWORD, project, key, value)


# ---------------------------------------------------------------------------

def test_add_to_group_persists(tmp_store):
    _seed(tmp_store, "alpha")
    add_to_group(tmp_store, PASSWORD, "backend", "alpha")
    groups = list_groups(tmp_store, PASSWORD)
    assert "backend" in groups
    assert "alpha" in groups["backend"]


def test_add_to_group_idempotent(tmp_store):
    _seed(tmp_store, "alpha")
    add_to_group(tmp_store, PASSWORD, "backend", "alpha")
    add_to_group(tmp_store, PASSWORD, "backend", "alpha")
    assert list_groups(tmp_store, PASSWORD)["backend"].count("alpha") == 1


def test_add_to_group_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        add_to_group(tmp_store, PASSWORD, "backend", "ghost")


def test_multiple_projects_in_group(tmp_store):
    _seed(tmp_store, "alpha")
    _seed(tmp_store, "beta")
    add_to_group(tmp_store, PASSWORD, "backend", "alpha")
    add_to_group(tmp_store, PASSWORD, "backend", "beta")
    members = projects_in_group(tmp_store, PASSWORD, "backend")
    assert set(members) == {"alpha", "beta"}


def test_remove_from_group(tmp_store):
    _seed(tmp_store, "alpha")
    add_to_group(tmp_store, PASSWORD, "backend", "alpha")
    remove_from_group(tmp_store, PASSWORD, "backend", "alpha")
    groups = list_groups(tmp_store, PASSWORD)
    assert "backend" not in groups  # empty group is pruned


def test_remove_from_group_missing_group_raises(tmp_store):
    with pytest.raises(KeyError, match="nonexistent"):
        remove_from_group(tmp_store, PASSWORD, "nonexistent", "alpha")


def test_remove_from_group_missing_project_raises(tmp_store):
    _seed(tmp_store, "alpha")
    _seed(tmp_store, "beta")
    add_to_group(tmp_store, PASSWORD, "backend", "alpha")
    with pytest.raises(KeyError, match="beta"):
        remove_from_group(tmp_store, PASSWORD, "backend", "beta")


def test_projects_in_group_missing_group_raises(tmp_store):
    with pytest.raises(KeyError, match="nope"):
        projects_in_group(tmp_store, PASSWORD, "nope")


def test_delete_group_returns_member_count(tmp_store):
    _seed(tmp_store, "alpha")
    _seed(tmp_store, "beta")
    add_to_group(tmp_store, PASSWORD, "backend", "alpha")
    add_to_group(tmp_store, PASSWORD, "backend", "beta")
    count = delete_group(tmp_store, PASSWORD, "backend")
    assert count == 2


def test_delete_group_removes_entry(tmp_store):
    _seed(tmp_store, "alpha")
    add_to_group(tmp_store, PASSWORD, "backend", "alpha")
    delete_group(tmp_store, PASSWORD, "backend")
    assert "backend" not in list_groups(tmp_store, PASSWORD)


def test_delete_group_missing_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        delete_group(tmp_store, PASSWORD, "ghost")


def test_list_groups_empty_initially(tmp_store):
    assert list_groups(tmp_store, PASSWORD) == {}
