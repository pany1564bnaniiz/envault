"""Ensure complexity internal keys do not leak into public project views."""

from __future__ import annotations

import pytest

from envault.projects import set_env, get_all_env
from envault.storage import list_projects
from envault.export import export_env
from envault.complexity import compute_complexity


@pytest.fixture()
def seeded_store(tmp_path):
    sp = tmp_path / "vault.enc"
    set_env("proj", "REAL_KEY", "real_value", "pw", store_path=sp)
    return sp


def test_complexity_key_not_in_list_projects(seeded_store):
    """The internal __complexity_config__ key must not appear as a project."""
    projects = list_projects("pw", path=seeded_store)
    assert "__complexity_config__" not in projects


def test_real_project_in_list_projects(seeded_store):
    assert "proj" in list_projects("pw", path=seeded_store)


def test_get_all_env_excludes_internal_complexity_keys(seeded_store):
    env = get_all_env("proj", "pw", store_path=seeded_store)
    for key in env:
        assert not key.startswith("__"), f"Internal key leaked: {key}"


def test_get_all_env_contains_real_key(seeded_store):
    env = get_all_env("proj", "pw", store_path=seeded_store)
    assert "REAL_KEY" in env


def test_export_env_excludes_internal_keys(seeded_store):
    output = export_env("proj", "pw", store_path=seeded_store)
    assert "__" not in output


def test_export_env_contains_real_key(seeded_store):
    output = export_env("proj", "pw", store_path=seeded_store)
    assert "REAL_KEY" in output
