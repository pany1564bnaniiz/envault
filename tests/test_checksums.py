"""Tests for envault.checksums."""

import pytest

from envault.checksums import (
    delete_checksum,
    get_checksum,
    list_checksums,
    save_checksum,
    verify_checksum,
)
from envault.projects import set_env
from envault.storage import save_store

PASSWORD = "test-secret"


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, PASSWORD, {})
    # seed a project
    set_env(path, PASSWORD, "myapp", "KEY", "value")
    return path


def _env(tmp_store):
    from envault.projects import get_all_env
    return get_all_env(tmp_store, PASSWORD, "myapp")


def test_save_checksum_returns_hex_digest(tmp_store):
    env = _env(tmp_store)
    digest = save_checksum(tmp_store, PASSWORD, "myapp", env)
    assert isinstance(digest, str)
    assert len(digest) == 64  # SHA-256 hex


def test_get_checksum_returns_none_when_not_set(tmp_store):
    assert get_checksum(tmp_store, PASSWORD, "nonexistent") is None


def test_get_checksum_returns_stored_digest(tmp_store):
    env = _env(tmp_store)
    digest = save_checksum(tmp_store, PASSWORD, "myapp", env)
    assert get_checksum(tmp_store, PASSWORD, "myapp") == digest


def test_verify_checksum_true_when_env_unchanged(tmp_store):
    env = _env(tmp_store)
    save_checksum(tmp_store, PASSWORD, "myapp", env)
    assert verify_checksum(tmp_store, PASSWORD, "myapp", env) is True


def test_verify_checksum_false_when_env_changed(tmp_store):
    env = _env(tmp_store)
    save_checksum(tmp_store, PASSWORD, "myapp", env)
    tampered = dict(env, KEY="different_value")
    assert verify_checksum(tmp_store, PASSWORD, "myapp", tampered) is False


def test_verify_checksum_false_when_no_checksum_stored(tmp_store):
    env = _env(tmp_store)
    assert verify_checksum(tmp_store, PASSWORD, "myapp", env) is False


def test_delete_checksum_returns_true_when_exists(tmp_store):
    env = _env(tmp_store)
    save_checksum(tmp_store, PASSWORD, "myapp", env)
    assert delete_checksum(tmp_store, PASSWORD, "myapp") is True
    assert get_checksum(tmp_store, PASSWORD, "myapp") is None


def test_delete_checksum_returns_false_when_missing(tmp_store):
    assert delete_checksum(tmp_store, PASSWORD, "ghost") is False


def test_list_checksums_empty_initially(tmp_store):
    assert list_checksums(tmp_store, PASSWORD) == {}


def test_list_checksums_shows_all_projects(tmp_store):
    from envault.projects import set_env
    set_env(tmp_store, PASSWORD, "other", "X", "1")
    from envault.projects import get_all_env
    env_a = get_all_env(tmp_store, PASSWORD, "myapp")
    env_b = get_all_env(tmp_store, PASSWORD, "other")
    save_checksum(tmp_store, PASSWORD, "myapp", env_a)
    save_checksum(tmp_store, PASSWORD, "other", env_b)
    result = list_checksums(tmp_store, PASSWORD)
    assert set(result.keys()) == {"myapp", "other"}
    assert all(len(v) == 64 for v in result.values())
