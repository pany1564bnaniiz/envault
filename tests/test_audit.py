"""Tests for envault.audit module."""

import json
import stat
from pathlib import Path

import pytest

import envault.audit as audit_mod


@pytest.fixture(autouse=True)
def tmp_audit_log(tmp_path, monkeypatch):
    """Redirect the audit log to a temporary directory for each test."""
    log_path = tmp_path / ".envault" / "audit.log"
    monkeypatch.setattr(audit_mod, "_AUDIT_LOG_PATH", log_path)
    yield log_path


def test_record_creates_log_file(tmp_audit_log):
    audit_mod.record("set", "myproject", key="DB_URL")
    assert tmp_audit_log.exists()


def test_record_entry_fields(tmp_audit_log):
    audit_mod.record("set", "myproject", key="API_KEY", detail="created")
    lines = tmp_audit_log.read_text().strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["action"] == "set"
    assert entry["project"] == "myproject"
    assert entry["key"] == "API_KEY"
    assert entry["detail"] == "created"
    assert "timestamp" in entry


def test_record_multiple_entries(tmp_audit_log):
    audit_mod.record("set", "proj", key="FOO")
    audit_mod.record("get", "proj", key="FOO")
    audit_mod.record("delete", "proj", key="FOO")
    entries = audit_mod.read_log()
    assert len(entries) == 3
    # newest first
    assert entries[0]["action"] == "delete"
    assert entries[1]["action"] == "get"
    assert entries[2]["action"] == "set"


def test_read_log_empty_when_no_file(tmp_audit_log):
    assert not tmp_audit_log.exists()
    assert audit_mod.read_log() == []


def test_read_log_limit(tmp_audit_log):
    for i in range(10):
        audit_mod.record("set", "proj", key=f"KEY_{i}")
    entries = audit_mod.read_log(limit=3)
    assert len(entries) == 3
    assert entries[0]["key"] == "KEY_9"


def test_log_file_permissions(tmp_audit_log):
    audit_mod.record("set", "proj", key="SECRET")
    mode = stat.S_IMODE(tmp_audit_log.stat().st_mode)
    assert mode == 0o600


def test_clear_log(tmp_audit_log):
    audit_mod.record("set", "proj", key="X")
    assert tmp_audit_log.exists()
    audit_mod.clear_log()
    assert not tmp_audit_log.exists()


def test_record_without_optional_fields(tmp_audit_log):
    audit_mod.record("list", "proj")
    entry = json.loads(tmp_audit_log.read_text().strip())
    assert "key" not in entry
    assert "detail" not in entry
