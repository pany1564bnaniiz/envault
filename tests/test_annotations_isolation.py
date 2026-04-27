"""Ensure annotations metadata does not leak into env exports or project listings."""

from __future__ import annotations

import pytest

from envault.annotations import set_annotation
from envault.projects import set_env, get_all_env
from envault.export import export_env
from envault.storage import save_store, list_projects


@pytest.fixture()
def seeded_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, "pw", {})
    set_env(path, "pw", "proj", "TOKEN", "tok123")
    set_annotation(path, "pw", "proj", "TOKEN", "Auth token")
    return path


def test_annotations_key_not_in_list_projects(seeded_store):
    projects = list_projects(seeded_store, "pw")
    assert "__annotations__" not in projects
    assert "proj" in projects


def test_get_all_env_excludes_annotations_key(seeded_store):
    env = get_all_env(seeded_store, "pw", "proj")
    assert "__annotations__" not in env


def test_get_all_env_contains_real_key(seeded_store):
    env = get_all_env(seeded_store, "pw", "proj")
    assert env["TOKEN"] == "tok123"


def test_export_env_excludes_annotations_key(seeded_store):
    content = export_env(seeded_store, "pw", "proj")
    assert "__annotations__" not in content


def test_export_env_contains_real_key(seeded_store):
    content = export_env(seeded_store, "pw", "proj")
    assert "TOKEN" in content
    assert "tok123" in content
