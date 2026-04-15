"""Password rotation for the envault store.

Re-encrypts all stored project data under a new master password.
"""

from __future__ import annotations

from typing import Any

from envault.storage import load_store, save_store
from envault.audit import record


def rotate_password(store_path: str, old_password: str, new_password: str) -> int:
    """Re-encrypt the entire store with *new_password*.

    Parameters
    ----------
    store_path:
        Filesystem path to the encrypted store file.
    old_password:
        Current master password used to decrypt the store.
    new_password:
        Replacement master password used to re-encrypt the store.

    Returns
    -------
    int
        Number of projects that were re-encrypted.

    Raises
    ------
    ValueError
        If *old_password* is wrong (propagated from :func:`load_store`).
    ValueError
        If *new_password* is empty.
    """
    if not new_password:
        raise ValueError("New password must not be empty.")

    # Will raise ValueError / InvalidToken if old_password is wrong.
    data: dict[str, Any] = load_store(store_path, old_password)

    project_count = len(data)

    # Persist the same plaintext data encrypted with the new password.
    save_store(store_path, new_password, data)

    record("rotate", "__store__", f"re-encrypted {project_count} project(s)")

    return project_count
