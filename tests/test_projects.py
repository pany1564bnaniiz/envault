"""Tests for envault.projects module."""

from __future__ import annotations

import pytest

from envault import projects as proj
from envault.storage import _store_path

PASSWORD = "test-secret-42"


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    """Redirect the storage file to a temporary directory for every test."""
    monkeypatch.setattr(
        "envault.storage._store_path",
        lambda: tmp_path / "envault_store.enc",
    )
    yield


def test_set_and_get_env():
    proj.set_env("myapp", "DB_URL", "postgres://localhost/db", PASSWORD)
    assert proj.get_env("myapp", "DB_URL", PASSWORD) == "postgres://localhost/db"


def test_set_multiple_keys():
    proj.set_env("myapp", "KEY_A", "alpha", PASSWORD)
    proj.set_env("myapp", "KEY_B", "beta", PASSWORD)
    env = proj.get_all_env("myapp", PASSWORD)
    assert env == {"KEY_A": "alpha", "KEY_B": "beta"}


def test_update_existing_key():
    proj.set_env("myapp", "TOKEN", "old", PASSWORD)
    proj.set_env("myapp", "TOKEN", "new", PASSWORD)
    assert proj.get_env("myapp", "TOKEN", PASSWORD) == "new"


def test_get_env_missing_project_raises():
    with pytest.raises(KeyError, match="ghost"):
        proj.get_env("ghost", "ANY", PASSWORD)


def test_get_env_missing_key_raises():
    proj.set_env("myapp", "PRESENT", "yes", PASSWORD)
    with pytest.raises(KeyError, match="ABSENT"):
        proj.get_env("myapp", "ABSENT", PASSWORD)


def test_delete_env_removes_key():
    proj.set_env("myapp", "TEMP", "value", PASSWORD)
    proj.delete_env("myapp", "TEMP", PASSWORD)
    with pytest.raises(KeyError):
        proj.get_env("myapp", "TEMP", PASSWORD)


def test_delete_env_missing_key_raises():
    proj.set_env("myapp", "REAL", "val", PASSWORD)
    with pytest.raises(KeyError, match="FAKE"):
        proj.delete_env("myapp", "FAKE", PASSWORD)


def test_delete_project():
    proj.set_env("doomed", "X", "1", PASSWORD)
    proj.delete_project("doomed", PASSWORD)
    with pytest.raises(KeyError, match="doomed"):
        proj.get_all_env("doomed", PASSWORD)


def test_delete_project_missing_raises():
    with pytest.raises(KeyError, match="nowhere"):
        proj.delete_project("nowhere", PASSWORD)


def test_multiple_projects_isolated():
    proj.set_env("alpha", "VAR", "from-alpha", PASSWORD)
    proj.set_env("beta", "VAR", "from-beta", PASSWORD)
    assert proj.get_env("alpha", "VAR", PASSWORD) == "from-alpha"
    assert proj.get_env("beta", "VAR", PASSWORD) == "from-beta"
