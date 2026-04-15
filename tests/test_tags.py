"""Unit tests for envault.tags."""

from __future__ import annotations

import pytest

from envault.storage import save_store
from envault.tags import add_tag, list_tags, remove_tag, projects_by_tag


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "store.enc")
    # Seed two projects with one env key each so they exist in the store.
    store = {
        "alpha": {"DB_URL": "postgres://localhost/alpha"},
        "beta": {"API_KEY": "secret"},
    }
    save_store(path, "pass", store)
    return path


def test_add_tag_persists(tmp_store):
    add_tag(tmp_store, "pass", "alpha", "production")
    assert "production" in list_tags(tmp_store, "pass", "alpha")


def test_add_tag_idempotent(tmp_store):
    add_tag(tmp_store, "pass", "alpha", "staging")
    add_tag(tmp_store, "pass", "alpha", "staging")  # second call must not duplicate
    assert list_tags(tmp_store, "pass", "alpha").count("staging") == 1


def test_add_tag_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        add_tag(tmp_store, "pass", "ghost", "prod")


def test_remove_tag(tmp_store):
    add_tag(tmp_store, "pass", "alpha", "old")
    remove_tag(tmp_store, "pass", "alpha", "old")
    assert "old" not in list_tags(tmp_store, "pass", "alpha")


def test_remove_tag_not_present_raises(tmp_store):
    with pytest.raises(KeyError, match="nonexistent"):
        remove_tag(tmp_store, "pass", "alpha", "nonexistent")


def test_list_tags_sorted(tmp_store):
    for t in ["zzz", "aaa", "mmm"]:
        add_tag(tmp_store, "pass", "alpha", t)
    result = list_tags(tmp_store, "pass", "alpha")
    assert result == sorted(result)


def test_list_tags_empty_by_default(tmp_store):
    assert list_tags(tmp_store, "pass", "beta") == []


def test_projects_by_tag(tmp_store):
    add_tag(tmp_store, "pass", "alpha", "team-a")
    add_tag(tmp_store, "pass", "beta", "team-a")
    result = projects_by_tag(tmp_store, "pass", "team-a")
    assert result == ["alpha", "beta"]


def test_projects_by_tag_no_match(tmp_store):
    assert projects_by_tag(tmp_store, "pass", "unknown-tag") == []


def test_tags_isolated_between_projects(tmp_store):
    add_tag(tmp_store, "pass", "alpha", "only-alpha")
    assert "only-alpha" not in list_tags(tmp_store, "pass", "beta")
