"""Tests for envault.lock session-locking feature."""

import time
from pathlib import Path

import pytest

import envault.lock as lock_mod


@pytest.fixture(autouse=True)
def tmp_lock(tmp_path, monkeypatch):
    """Redirect the lock file to a temp directory for each test."""
    lock_file = tmp_path / "session.lock"
    monkeypatch.setattr(lock_mod, "_LOCK_FILE", lock_file)
    yield lock_file
    # cleanup
    if lock_file.exists():
        lock_file.unlink()


def test_vault_not_locked_initially():
    assert not lock_mod.is_locked()


def test_lock_vault_creates_file(tmp_lock):
    lock_mod.lock_vault()
    assert tmp_lock.exists()


def test_lock_vault_sets_permissions(tmp_lock):
    lock_mod.lock_vault()
    mode = oct(tmp_lock.stat().st_mode)[-3:]
    assert mode == "600"


def test_is_locked_after_lock(tmp_lock):
    lock_mod.lock_vault()
    assert lock_mod.is_locked()


def test_unlock_removes_file(tmp_lock):
    lock_mod.lock_vault()
    lock_mod.unlock_vault()
    assert not lock_mod.is_locked()


def test_unlock_idempotent():
    # Should not raise even if already unlocked
    lock_mod.unlock_vault()
    lock_mod.unlock_vault()


def test_locked_at_returns_none_when_unlocked():
    assert lock_mod.locked_at() is None


def test_locked_at_returns_timestamp():
    before = time.time()
    lock_mod.lock_vault()
    ts = lock_mod.locked_at()
    after = time.time()
    assert ts is not None
    assert before <= ts <= after


def test_auto_lock_if_idle_locks_open_vault(tmp_lock):
    # Vault is open (no lock file) — auto_lock_if_idle should lock it
    result = lock_mod.auto_lock_if_idle(timeout_seconds=60)
    assert result is True
    assert lock_mod.is_locked()


def test_auto_lock_if_idle_skips_already_locked():
    lock_mod.lock_vault()
    result = lock_mod.auto_lock_if_idle(timeout_seconds=60)
    assert result is False
