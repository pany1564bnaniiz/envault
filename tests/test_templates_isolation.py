"""Ensure templates are isolated from regular project data."""

from __future__ import annotations

import pytest

from envault.templates import save_template, list_templates
from envault.projects import set_env, get_all_env
from envault.storage import list_projects
from envault.export import export_env


@pytest.fixture()
def seeded_store(tmp_path):
    path = str(tmp_path / "store.enc")
    password = "iso-pass"
    set_env(path, password, "app", "REAL_KEY", "real-value")
    save_template(path, password, "my-tmpl", {"TMPL_KEY": "tmpl-value"})
    return path, password


def test_templates_not_in_list_projects(seeded_store):
    path, password = seeded_store
    projects = list_projects(path, password)
    assert "__templates__" not in projects


def test_real_project_in_list_projects(seeded_store):
    path, password = seeded_store
    assert "app" in list_projects(path, password)


def test_get_all_env_excludes_template_keys(seeded_store):
    path, password = seeded_store
    env = get_all_env(path, password, "app")
    assert "TMPL_KEY" not in env
    assert "REAL_KEY" in env


def test_export_excludes_template_keys(seeded_store):
    path, password = seeded_store
    output = export_env(path, password, "app")
    assert "TMPL_KEY" not in output
    assert "REAL_KEY" in output


def test_multiple_templates_all_listed(seeded_store):
    path, password = seeded_store
    save_template(path, password, "second", {"S": "1"})
    names = list_templates(path, password)
    assert "my-tmpl" in names
    assert "second" in names
    assert len(names) == 2
