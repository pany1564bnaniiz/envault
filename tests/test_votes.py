"""Tests for envault.votes."""

from __future__ import annotations

import os
import pytest

from envault.storage import save_store, load_store
from envault.projects import set_env
from envault.votes import downvote, get_voters, get_votes, top_projects, upvote


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.enc")


def _seed(store_path: str, password: str = "pw") -> None:
    set_env(store_path, password, "alpha", "KEY", "val")
    set_env(store_path, password, "beta", "KEY", "val")


def test_upvote_returns_count(tmp_store):
    _seed(tmp_store)
    count = upvote(tmp_store, "pw", "alpha", "alice")
    assert count == 1


def test_upvote_idempotent(tmp_store):
    _seed(tmp_store)
    upvote(tmp_store, "pw", "alpha", "alice")
    count = upvote(tmp_store, "pw", "alpha", "alice")
    assert count == 1


def test_multiple_voters(tmp_store):
    _seed(tmp_store)
    upvote(tmp_store, "pw", "alpha", "alice")
    count = upvote(tmp_store, "pw", "alpha", "bob")
    assert count == 2


def test_get_votes_zero_when_none(tmp_store):
    _seed(tmp_store)
    assert get_votes(tmp_store, "pw", "alpha") == 0


def test_get_voters_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert get_voters(tmp_store, "pw", "alpha") == []


def test_get_voters_after_upvote(tmp_store):
    _seed(tmp_store)
    upvote(tmp_store, "pw", "alpha", "alice")
    assert "alice" in get_voters(tmp_store, "pw", "alpha")


def test_downvote_removes_voter(tmp_store):
    _seed(tmp_store)
    upvote(tmp_store, "pw", "alpha", "alice")
    count = downvote(tmp_store, "pw", "alpha", "alice")
    assert count == 0
    assert "alice" not in get_voters(tmp_store, "pw", "alpha")


def test_downvote_non_voter_is_noop(tmp_store):
    _seed(tmp_store)
    count = downvote(tmp_store, "pw", "alpha", "ghost")
    assert count == 0


def test_upvote_missing_project_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError, match="missing"):
        upvote(tmp_store, "pw", "missing", "alice")


def test_top_projects_sorted(tmp_store):
    _seed(tmp_store)
    upvote(tmp_store, "pw", "alpha", "alice")
    upvote(tmp_store, "pw", "alpha", "bob")
    upvote(tmp_store, "pw", "beta", "carol")
    results = top_projects(tmp_store, "pw")
    assert results[0]["project"] == "alpha"
    assert results[0]["count"] == 2


def test_top_projects_respects_limit(tmp_store):
    _seed(tmp_store)
    upvote(tmp_store, "pw", "alpha", "alice")
    upvote(tmp_store, "pw", "beta", "bob")
    results = top_projects(tmp_store, "pw", n=1)
    assert len(results) == 1


def test_top_projects_empty_when_no_votes(tmp_store):
    _seed(tmp_store)
    assert top_projects(tmp_store, "pw") == []
