"""Audit log for tracking envault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_AUDIT_LOG_PATH = Path.home() / ".envault" / "audit.log"


def _log_path() -> Path:
    return _AUDIT_LOG_PATH


def record(action: str, project: str, key: Optional[str] = None, detail: Optional[str] = None) -> None:
    """Append a single audit entry to the log file."""
    log_path = _log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "project": project,
    }
    if key is not None:
        entry["key"] = key
    if detail is not None:
        entry["detail"] = detail

    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")

    # Restrict permissions on first write or subsequent writes
    os.chmod(log_path, 0o600)


def read_log(limit: int = 50) -> list[dict]:
    """Return the last *limit* audit entries, newest first."""
    log_path = _log_path()
    if not log_path.exists():
        return []

    with open(log_path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    entries = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return list(reversed(entries[-limit:]))


def clear_log() -> None:
    """Delete the audit log file entirely."""
    log_path = _log_path()
    if log_path.exists():
        log_path.unlink()
