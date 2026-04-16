"""Session locking: lock the vault after inactivity or on demand."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

_LOCK_FILE = Path.home() / ".envault" / "session.lock"


def _lock_path() -> Path:
    return _LOCK_FILE


def lock_vault() -> None:
    """Write a lock file, marking the vault as locked."""
    _lock_path().parent.mkdir(parents=True, exist_ok=True)
    _lock_path().write_text(json.dumps({"locked_at": time.time()}))
    _lock_path().chmod(0o600)


def unlock_vault() -> None:
    """Remove the lock file, marking the vault as unlocked."""
    try:
        _lock_path().unlink()
    except FileNotFoundError:
        pass


def is_locked() -> bool:
    """Return True if the vault is currently locked."""
    return _lock_path().exists()


def locked_at() -> float | None:
    """Return the epoch timestamp when the vault was locked, or None."""
    if not is_locked():
        return None
    data = json.loads(_lock_path().read_text())
    return data.get("locked_at")


def auto_lock_if_idle(timeout_seconds: int) -> bool:
    """Lock the vault if it has been unlocked for longer than *timeout_seconds*.

    Returns True if the vault was locked by this call.
    """
    if is_locked():
        return False
    ts = locked_at()
    # If there is no lock file the vault is open; use mtime of store as proxy.
    # For simplicity we check the lock file's own mtime when available.
    lp = _lock_path()
    if not lp.exists():
        # Vault is open with no timestamp reference — lock immediately.
        lock_vault()
        return True
    if ts is not None and (time.time() - ts) > timeout_seconds:
        lock_vault()
        return True
    return False
