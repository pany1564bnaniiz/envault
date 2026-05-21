"""Ensure vote metadata does not bleed into project/env listings."""

from __future__ import annotations

import pytest

from envault.export import export_env
from envault.projects import get_all_env
from envault.storage import list_projects
from envault.votes import upvote, _VOTES_KEY
from envault.projects import set_env


@pytest.fixture()
def seeded_store(tmp_path):
    p = str(tmp_path / "vault.enc")
    set_env(p, "pw", "proj", "API_KEY", "abc123")
    upvote(p, "pw", "proj", "alice")
    return p


def test_votes_key_not_in_list_projects(seeded_store):
    projects = list_projects(seeded_store, "pw")
    assert _VOTES_KEY not in projects


def test_real_project_in_list_projects(seeded_store):
    projects = list_projects(seeded_store, "pw")
    assert "proj" in projects


def test_get_all_env_excludes_votes_key(seeded_store):
    env = get_all_env(seeded_store, "pw", "proj")
    assert _VOTES_KEY not in env


def test_get_all_env_contains_real_key(seeded_store):
    env = get_all_env(seeded_store, "pw", "proj")
    assert "API_KEY" in env


def test_export_env_excludes_votes_key(seeded_store):
    output = export_env(seeded_store, "pw", "proj")
    assert _VOTES_KEY not in output


def test_export_env_contains_real_key(seeded_store):
    output = export_env(seeded_store, "pw", "proj")
    assert "API_KEY" in output
