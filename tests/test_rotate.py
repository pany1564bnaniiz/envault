"""Tests for envault.rotate (password rotation)."""

from __future__ import annotations

import pytest

from envault.rotate import rotate_password
from envault.storage import load_store, save_store


@pytest.fixture()
def tmp_store(tmp_path):
    """Return a helper that creates a pre-populated store file."""
    path = str(tmp_path / "store.enc")

    def _make(password: str = "old-pass", data: dict | None = None) -> str:
        payload = data if data is not None else {"proj": {"KEY": "value"}}
        save_store(path, password, payload)
        return path

    return _make


def test_rotate_returns_project_count(tmp_store):
    path = tmp_store(data={"alpha": {"A": "1"}, "beta": {"B": "2"}})
    count = rotate_password(path, "old-pass", "new-pass")
    assert count == 2


def test_rotate_data_survives_with_new_password(tmp_store):
    original = {"myproject": {"DB_URL": "postgres://localhost/db"}}
    path = tmp_store(data=original)
    rotate_password(path, "old-pass", "new-pass")
    loaded = load_store(path, "new-pass")
    assert loaded == original


def test_rotate_old_password_no_longer_works(tmp_store):
    path = tmp_store()
    rotate_password(path, "old-pass", "new-pass")
    with pytest.raises(Exception):
        load_store(path, "old-pass")


def test_rotate_wrong_old_password_raises(tmp_store):
    path = tmp_store()
    with pytest.raises((ValueError, Exception)):
        rotate_password(path, "wrong-pass", "new-pass")


def test_rotate_empty_new_password_raises(tmp_store):
    path = tmp_store()
    with pytest.raises(ValueError, match="empty"):
        rotate_password(path, "old-pass", "")


def test_rotate_empty_store(tmp_store):
    path = tmp_store(data={})
    count = rotate_password(path, "old-pass", "new-pass")
    assert count == 0
    assert load_store(path, "new-pass") == {}
