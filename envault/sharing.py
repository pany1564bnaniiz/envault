"""Sharing: export/import encrypted project bundles for sharing between users."""
from __future__ import annotations
import json
import os
import base64
from pathlib import Path
from envault.crypto import encrypt, decrypt
from envault.projects import get_all_env
from envault.storage import load_store, save_store


def export_bundle(store_path: Path, password: str, project: str, bundle_password: str) -> str:
    """Encrypt project env vars with a bundle password and return base64 bundle string."""
    env = get_all_env(store_path, password, project)
    payload = json.dumps(env)
    token = encrypt(bundle_password, payload)
    return base64.urlsafe_b64encode(token.encode()).decode()


def import_bundle(store_path: Path, password: str, project: str, bundle: str, bundle_password: str) -> int:
    """Decrypt a bundle and merge keys into the given project. Returns number of keys imported."""
    raw = base64.urlsafe_b64decode(bundle.encode()).decode()
    payload = decrypt(bundle_password, raw)
    env: dict[str, str] = json.loads(payload)

    store = load_store(store_path, password)
    if project not in store:
        store[project] = {}
    store[project].update(env)
    save_store(store_path, password, store)
    return len(env)


def list_bundle_keys(bundle: str, bundle_password: str) -> list[str]:
    """Peek at the keys inside a bundle without importing."""
    raw = base64.urlsafe_b64decode(bundle.encode()).decode()
    payload = decrypt(bundle_password, raw)
    env: dict[str, str] = json.loads(payload)
    return sorted(env.keys())
