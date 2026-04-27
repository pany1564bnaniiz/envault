"""Tests for envault.reactions."""
from __future__ import annotations

import pytest

from envault.reactions import (
    add_reaction,
    list_reactions,
    reaction_summary,
    remove_reaction,
    projects_reacted_by,
)
from envault.projects import set_env


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "store.enc")


PASS = "s3cret"


def _seed(store: str, project: str = "alpha") -> None:
    set_env(store, PASS, project, "KEY", "val")


def test_add_reaction_persists(tmp_store):
    _seed(tmp_store)
    add_reaction(tmp_store, PASS, "alpha", "👍")
    result = list_reactions(tmp_store, PASS, "alpha")
    assert "👍" in result
    assert "user" in result["👍"]


def test_add_reaction_idempotent(tmp_store):
    _seed(tmp_store)
    add_reaction(tmp_store, PASS, "alpha", "🔥", actor="alice")
    add_reaction(tmp_store, PASS, "alpha", "🔥", actor="alice")
    result = list_reactions(tmp_store, PASS, "alpha")
    assert result["🔥"].count("alice") == 1


def test_add_reaction_multiple_actors(tmp_store):
    _seed(tmp_store)
    add_reaction(tmp_store, PASS, "alpha", "❤️", actor="alice")
    add_reaction(tmp_store, PASS, "alpha", "❤️", actor="bob")
    result = list_reactions(tmp_store, PASS, "alpha")
    assert set(result["❤️"]) == {"alice", "bob"}


def test_add_reaction_invalid_emoji_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="Invalid reaction"):
        add_reaction(tmp_store, PASS, "alpha", "😈")


def test_add_reaction_missing_project_raises(tmp_store):
    with pytest.raises(KeyError):
        add_reaction(tmp_store, PASS, "ghost", "👍")


def test_remove_reaction(tmp_store):
    _seed(tmp_store)
    add_reaction(tmp_store, PASS, "alpha", "👍", actor="alice")
    remove_reaction(tmp_store, PASS, "alpha", "👍", actor="alice")
    result = list_reactions(tmp_store, PASS, "alpha")
    assert "alice" not in result.get("👍", [])


def test_remove_reaction_nonexistent_is_noop(tmp_store):
    _seed(tmp_store)
    remove_reaction(tmp_store, PASS, "alpha", "👍", actor="nobody")


def test_reaction_summary(tmp_store):
    _seed(tmp_store)
    add_reaction(tmp_store, PASS, "alpha", "🚀", actor="alice")
    add_reaction(tmp_store, PASS, "alpha", "🚀", actor="bob")
    add_reaction(tmp_store, PASS, "alpha", "✅", actor="carol")
    summary = reaction_summary(tmp_store, PASS, "alpha")
    assert summary["🚀"] == 2
    assert summary["✅"] == 1


def test_list_reactions_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert list_reactions(tmp_store, PASS, "alpha") == {}


def test_projects_reacted_by(tmp_store):
    _seed(tmp_store, "alpha")
    _seed(tmp_store, "beta")
    add_reaction(tmp_store, PASS, "alpha", "👍", actor="alice")
    add_reaction(tmp_store, PASS, "beta", "🔥", actor="alice")
    result = projects_reacted_by(tmp_store, PASS, "alice")
    assert result == ["alpha", "beta"]


def test_projects_reacted_by_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert projects_reacted_by(tmp_store, PASS, "nobody") == []
