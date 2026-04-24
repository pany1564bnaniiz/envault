"""Checksums: track content hashes for project env vars to detect external tampering."""

import hashlib
import json
from typing import Optional

from envault.storage import load_store, save_store

_CHECKSUM_KEY = "__checksums__"


def _checksums_map(store: dict) -> dict:
    return store.setdefault(_CHECKSUM_KEY, {})


def _compute_hash(env: dict) -> str:
    """Return a stable SHA-256 hex digest of the sorted env dict."""
    canonical = json.dumps(env, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def save_checksum(store_path: str, password: str, project: str, env: dict) -> str:
    """Compute and persist a checksum for *project*'s current env.

    Returns the hex digest that was stored.
    """
    store = load_store(store_path, password)
    digest = _compute_hash(env)
    _checksums_map(store)[project] = digest
    save_store(store_path, password, store)
    return digest


def get_checksum(store_path: str, password: str, project: str) -> Optional[str]:
    """Return the stored checksum for *project*, or None if not recorded."""
    store = load_store(store_path, password)
    return _checksums_map(store).get(project)


def verify_checksum(store_path: str, password: str, project: str, env: dict) -> bool:
    """Return True if *env* matches the stored checksum for *project*.

    Returns False if the checksum is missing or the digest does not match.
    """
    stored = get_checksum(store_path, password, project)
    if stored is None:
        return False
    return stored == _compute_hash(env)


def delete_checksum(store_path: str, password: str, project: str) -> bool:
    """Remove the stored checksum for *project*.

    Returns True if an entry was removed, False if it did not exist.
    """
    store = load_store(store_path, password)
    cmap = _checksums_map(store)
    if project not in cmap:
        return False
    del cmap[project]
    save_store(store_path, password, store)
    return True


def list_checksums(store_path: str, password: str) -> dict:
    """Return a mapping of {project: digest} for all recorded checksums."""
    store = load_store(store_path, password)
    return dict(_checksums_map(store))
