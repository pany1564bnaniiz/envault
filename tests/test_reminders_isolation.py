"""Ensure reminder metadata is isolated from project/export views."""
from __future__ import annotations

import time

import pytest

from envault.storage import save_store, list_projects
from envault.projects import get_all_env
from envault.export import export_env
from envault.reminders import set_reminder

_STORE = "vault.enc"
_PW = "pw"


@pytest.fixture()
def seeded_store(tmp_path):
    path = str(tmp_path / _STORE)
    save_store(path, _PW, {"proj": {"FOO": "bar"}})
    set_reminder(path, _PW, "proj", "check this", time.time() + 60)
    return path


def test_reminders_not_in_list_projects(seeded_store):
    projects = list_projects(seeded_store, _PW)
    assert "__reminders__" not in projects
    assert "proj" in projects


def test_get_all_env_excludes_reminders_key(seeded_store):
    env = get_all_env(seeded_store, _PW, "proj")
    assert "__reminders__" not in env


def test_get_all_env_contains_real_key(seeded_store):
    env = get_all_env(seeded_store, _PW, "proj")
    assert env.get("FOO") == "bar"


def test_export_env_excludes_reminders_key(seeded_store):
    content = export_env(seeded_store, _PW, "proj")
    assert "__reminders__" not in content


def test_export_env_contains_real_key(seeded_store):
    content = export_env(seeded_store, _PW, "proj")
    assert "FOO" in content
