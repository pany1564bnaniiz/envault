"""Tests for envault.dependencies."""

import pytest

from envault.storage import save_store
from envault.dependencies import (
    add_dependency,
    remove_dependency,
    list_dependencies,
    dependents_of,
    all_dependencies,
)


PASSWORD = "test-secret"


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    # Seed two projects
    store = {
        "alpha": {"API_KEY": "abc"},
        "beta": {"DB_URL": "postgres://localhost/beta"},
        "gamma": {"TOKEN": "xyz"},
    }
    save_store(path, PASSWORD, store)
    return path


def test_add_dependency_persists(tmp_store):
    add_dependency(tmp_store, PASSWORD, "beta", "alpha")
    deps = list_dependencies(tmp_store, PASSWORD, "beta")
    assert "alpha" in deps


def test_add_dependency_idempotent(tmp_store):
    add_dependency(tmp_store, PASSWORD, "beta", "alpha")
    add_dependency(tmp_store, PASSWORD, "beta", "alpha")
    deps = list_dependencies(tmp_store, PASSWORD, "beta")
    assert deps.count("alpha") == 1


def test_add_dependency_self_loop_raises(tmp_store):
    with pytest.raises(ValueError, match="cannot depend on itself"):
        add_dependency(tmp_store, PASSWORD, "alpha", "alpha")


def test_add_dependency_missing_project_raises(tmp_store):
    with pytest.raises(KeyError):
        add_dependency(tmp_store, PASSWORD, "nonexistent", "alpha")


def test_add_dependency_missing_target_raises(tmp_store):
    with pytest.raises(KeyError):
        add_dependency(tmp_store, PASSWORD, "alpha", "nonexistent")


def test_list_dependencies_empty_when_none(tmp_store):
    deps = list_dependencies(tmp_store, PASSWORD, "alpha")
    assert deps == []


def test_list_dependencies_multiple(tmp_store):
    add_dependency(tmp_store, PASSWORD, "gamma", "alpha")
    add_dependency(tmp_store, PASSWORD, "gamma", "beta")
    deps = list_dependencies(tmp_store, PASSWORD, "gamma")
    assert set(deps) == {"alpha", "beta"}


def test_remove_dependency(tmp_store):
    add_dependency(tmp_store, PASSWORD, "beta", "alpha")
    remove_dependency(tmp_store, PASSWORD, "beta", "alpha")
    deps = list_dependencies(tmp_store, PASSWORD, "beta")
    assert "alpha" not in deps


def test_remove_dependency_nonexistent_is_silent(tmp_store):
    # Should not raise
    remove_dependency(tmp_store, PASSWORD, "beta", "alpha")


def test_dependents_of(tmp_store):
    add_dependency(tmp_store, PASSWORD, "beta", "alpha")
    add_dependency(tmp_store, PASSWORD, "gamma", "alpha")
    result = dependents_of(tmp_store, PASSWORD, "alpha")
    assert set(result) == {"beta", "gamma"}


def test_dependents_of_empty_when_none(tmp_store):
    result = dependents_of(tmp_store, PASSWORD, "gamma")
    assert result == []


def test_all_dependencies_returns_only_nonempty(tmp_store):
    add_dependency(tmp_store, PASSWORD, "beta", "alpha")
    mapping = all_dependencies(tmp_store, PASSWORD)
    assert "beta" in mapping
    assert "alpha" not in mapping  # alpha has no deps
    assert "gamma" not in mapping
