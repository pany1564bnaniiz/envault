"""Verify that tag metadata does not pollute env-variable exports.

Tags are stored under the reserved '__tags__' key inside a project dict.
This file ensures that key never surfaces through the normal env-access
APIs (get_env, get_all_env, export_env).
"""

from __future__ import annotations

import pytest

from envault.export import export_env
from envault.projects import get_all_env, set_env
from envault.storage import save_store
from envault.tags import add_tag


@pytest.fixture()
def seeded_store(tmp_path):
    path = str(tmp_path / "store.enc")
    save_store(path, "pw", {})
    set_env(path, "pw", "app", "PORT", "8080")
    add_tag(path, "pw", "app", "production")
    return path


def test_get_all_env_excludes_tags_key(seeded_store):
    env = get_all_env(seeded_store, "pw", "app")
    assert "__tags__" not in env


def test_get_all_env_contains_real_key(seeded_store):
    env = get_all_env(seeded_store, "pw", "app")
    assert env["PORT"] == "8080"


def test_export_env_excludes_tags_key(seeded_store):
    output = export_env(seeded_store, "pw", "app")
    assert "__tags__" not in output


def test_export_env_contains_real_key(seeded_store):
    output = export_env(seeded_store, "pw", "app")
    assert "PORT" in output
    assert "8080" in output
