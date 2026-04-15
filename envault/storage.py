"""Local encrypted storage for envault — reads and writes .env data to disk."""

import json
import os
from pathlib import Path
from typing import Dict

from envault.crypto import encrypt, decrypt

DEFAULT_STORE_DIR = Path.home() / ".envault"
STORE_FILE = "store.enc"


def _store_path(store_dir: Path = DEFAULT_STORE_DIR) -> Path:
    store_dir.mkdir(parents=True, exist_ok=True)
    return store_dir / STORE_FILE


def load_store(password: str, store_dir: Path = DEFAULT_STORE_DIR) -> Dict[str, Dict[str, str]]:
    """Load and decrypt the envault store. Returns an empty dict if store doesn't exist."""
    path = _store_path(store_dir)
    if not path.exists():
        return {}
    encoded = path.read_text(encoding="utf-8").strip()
    if not encoded:
        return {}
    raw = decrypt(encoded, password)
    return json.loads(raw)


def save_store(
    data: Dict[str, Dict[str, str]],
    password: str,
    store_dir: Path = DEFAULT_STORE_DIR,
) -> None:
    """Encrypt and persist the envault store to disk."""
    path = _store_path(store_dir)
    raw = json.dumps(data)
    encoded = encrypt(raw, password)
    path.write_text(encoded, encoding="utf-8")
    os.chmod(path, 0o600)


def list_projects(password: str, store_dir: Path = DEFAULT_STORE_DIR) -> list:
    """Return a sorted list of project names in the store."""
    store = load_store(password, store_dir)
    return sorted(store.keys())
