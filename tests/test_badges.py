"""Tests for envault.badges."""

from __future__ import annotations

import pytest

from envault.badges import (
    add_badge,
    clear_badges,
    list_badges,
    projects_with_badge,
    remove_badge,
)
from envault.storage import save_store


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.db")
    return path


def _seed(store_path: str, password: str = "pw") -> None:
    """Create two projects in the store."""
    save_store(store_path, password, {"alpha": {"K": "V"}, "beta": {"X": "Y"}})


def test_add_badge_persists(tmp_store):
    _seed(tmp_store)
    add_badge(tmp_store, "pw", "alpha", "production")
    assert "production" in list_badges(tmp_store, "pw", "alpha")


def test_add_badge_idempotent(tmp_store):
    _seed(tmp_store)
    add_badge(tmp_store, "pw", "alpha", "stable")
    add_badge(tmp_store, "pw", "alpha", "stable")
    assert list_badges(tmp_store, "pw", "alpha").count("stable") == 1


def test_add_badge_invalid_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="Unknown badge"):
        add_badge(tmp_store, "pw", "alpha", "legendary")


def test_add_badge_missing_project_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError):
        add_badge(tmp_store, "pw", "nonexistent", "stable")


def test_remove_badge(tmp_store):
    _seed(tmp_store)
    add_badge(tmp_store, "pw", "alpha", "staging")
    removed = remove_badge(tmp_store, "pw", "alpha", "staging")
    assert removed is True
    assert "staging" not in list_badges(tmp_store, "pw", "alpha")


def test_remove_badge_not_present_returns_false(tmp_store):
    _seed(tmp_store)
    result = remove_badge(tmp_store, "pw", "alpha", "stable")
    assert result is False


def test_list_badges_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert list_badges(tmp_store, "pw", "alpha") == []


def test_list_badges_sorted(tmp_store):
    _seed(tmp_store)
    add_badge(tmp_store, "pw", "alpha", "stable")
    add_badge(tmp_store, "pw", "alpha", "production")
    badges = list_badges(tmp_store, "pw", "alpha")
    assert badges == sorted(badges)


def test_projects_with_badge(tmp_store):
    _seed(tmp_store)
    add_badge(tmp_store, "pw", "alpha", "production")
    add_badge(tmp_store, "pw", "beta", "production")
    projects = projects_with_badge(tmp_store, "pw", "production")
    assert "alpha" in projects
    assert "beta" in projects


def test_projects_with_badge_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert projects_with_badge(tmp_store, "pw", "deprecated") == []


def test_clear_badges_returns_count(tmp_store):
    _seed(tmp_store)
    add_badge(tmp_store, "pw", "alpha", "stable")
    add_badge(tmp_store, "pw", "alpha", "production")
    count = clear_badges(tmp_store, "pw", "alpha")
    assert count == 2
    assert list_badges(tmp_store, "pw", "alpha") == []


def test_clear_badges_on_empty_returns_zero(tmp_store):
    _seed(tmp_store)
    assert clear_badges(tmp_store, "pw", "alpha") == 0
