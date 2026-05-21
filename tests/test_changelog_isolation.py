"""Ensure changelog metadata does not leak into project env data."""

from __future__ import annotations

import pytest

from envault.storage import save_store
from envault.changelog import add_entry
from envault.projects import get_all_env
from envault.export import export_env


@pytest.fixture()
def seeded_store(tmp_path):
    path = tmp_path / "vault.enc"
    save_store(path, "pw", {"app": {"DB_URL": "postgres://localhost/app"}})
    add_entry(path, "pw", "app", "first entry")
    return path


def test_changelog_key_not_in_list_projects(seeded_store):
    from envault.storage import list_projects
    projects = list_projects(seeded_store, "pw")
    assert "__changelog__" not in projects


def test_get_all_env_excludes_changelog_key(seeded_store):
    env = get_all_env(seeded_store, "pw", "app")
    assert "__changelog__" not in env


def test_get_all_env_contains_real_key(seeded_store):
    env = get_all_env(seeded_store, "pw", "app")
    assert "DB_URL" in env


def test_export_env_excludes_changelog_key(seeded_store):
    output = export_env(seeded_store, "pw", "app")
    assert "__changelog__" not in output


def test_export_env_contains_real_key(seeded_store):
    output = export_env(seeded_store, "pw", "app")
    assert "DB_URL" in output
