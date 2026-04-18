"""Tests for envault.pin."""
import pytest
from pathlib import Path

from envault.storage import save_store, load_store
from envault.projects import set_env
from envault.pin import pin_project, unpin_project, list_pinned, is_pinned

PASSWORD = "testpass"


@pytest.fixture()
def tmp_store(tmp_path):
    p = tmp_path / "vault.db"
    save_store(p, PASSWORD, {})
    return p


def _seed(tmp_store, project: str):
    set_env(tmp_store, PASSWORD, project, "KEY", "val")


def test_pin_project_persists(tmp_store):
    _seed(tmp_store, "alpha")
    pin_project(tmp_store, PASSWORD, "alpha")
    assert is_pinned(tmp_store, PASSWORD, "alpha")


def test_pin_missing_project_raises(tmp_store):
    with pytest.raises(KeyError):
        pin_project(tmp_store, PASSWORD, "ghost")


def test_pin_idempotent(tmp_store):
    _seed(tmp_store, "alpha")
    pin_project(tmp_store, PASSWORD, "alpha")
    pin_project(tmp_store, PASSWORD, "alpha")
    assert list_pinned(tmp_store, PASSWORD).count("alpha") == 1


def test_unpin_removes_project(tmp_store):
    _seed(tmp_store, "alpha")
    pin_project(tmp_store, PASSWORD, "alpha")
    unpin_project(tmp_store, PASSWORD, "alpha")
    assert not is_pinned(tmp_store, PASSWORD, "alpha")


def test_unpin_noop_when_not_pinned(tmp_store):
    _seed(tmp_store, "alpha")
    unpin_project(tmp_store, PASSWORD, "alpha")  # should not raise
    assert list_pinned(tmp_store, PASSWORD) == []


def test_list_pinned_multiple(tmp_store):
    for name in ("alpha", "beta", "gamma"):
        _seed(tmp_store, name)
    pin_project(tmp_store, PASSWORD, "alpha")
    pin_project(tmp_store, PASSWORD, "gamma")
    pins = list_pinned(tmp_store, PASSWORD)
    assert "alpha" in pins
    assert "gamma" in pins
    assert "beta" not in pins


def test_pins_not_in_regular_project_list(tmp_store):
    from envault.storage import list_projects
    _seed(tmp_store, "alpha")
    pin_project(tmp_store, PASSWORD, "alpha")
    projects = list_projects(tmp_store, PASSWORD)
    assert "__pins__" not in projects
