"""Tests for envault.endorsements."""

from __future__ import annotations

import pytest

from envault.endorsements import (
    endorse,
    endorsement_counts,
    list_endorsements,
    withdraw,
)
from envault.storage import save_store


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.db")
    password = "testpass"
    return path, password


def _seed(tmp_store, project: str = "alpha"):
    path, password = tmp_store
    save_store(path, password, {project: {"KEY": "val"}})


# ---------------------------------------------------------------------------
# endorse
# ---------------------------------------------------------------------------

def test_endorse_returns_entry(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    entry = endorse(path, pw, "alpha", "secure", actor="alice")
    assert entry["actor"] == "alice"
    assert entry["quality"] == "secure"
    assert "endorsed_at" in entry


def test_endorse_persists(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    endorse(path, pw, "alpha", "reliable", actor="bob")
    counts = endorsement_counts(path, pw, "alpha")
    assert counts.get("reliable", 0) == 1


def test_endorse_idempotent(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    endorse(path, pw, "alpha", "minimal", actor="carol")
    endorse(path, pw, "alpha", "minimal", actor="carol")
    counts = endorsement_counts(path, pw, "alpha")
    assert counts["minimal"] == 1


def test_endorse_multiple_actors(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    endorse(path, pw, "alpha", "secure", actor="alice")
    endorse(path, pw, "alpha", "secure", actor="bob")
    counts = endorsement_counts(path, pw, "alpha")
    assert counts["secure"] == 2


def test_endorse_invalid_quality_raises(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    with pytest.raises(ValueError, match="Invalid quality"):
        endorse(path, pw, "alpha", "not-a-real-quality")


def test_endorse_missing_project_raises(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    with pytest.raises(KeyError):
        endorse(path, pw, "ghost", "secure")


# ---------------------------------------------------------------------------
# withdraw
# ---------------------------------------------------------------------------

def test_withdraw_returns_true_when_removed(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    endorse(path, pw, "alpha", "reliable", actor="alice")
    result = withdraw(path, pw, "alpha", "reliable", actor="alice")
    assert result is True


def test_withdraw_removes_entry(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    endorse(path, pw, "alpha", "reliable", actor="alice")
    withdraw(path, pw, "alpha", "reliable", actor="alice")
    counts = endorsement_counts(path, pw, "alpha")
    assert counts.get("reliable", 0) == 0


def test_withdraw_returns_false_when_not_found(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    result = withdraw(path, pw, "alpha", "reliable", actor="nobody")
    assert result is False


# ---------------------------------------------------------------------------
# list_endorsements / endorsement_counts
# ---------------------------------------------------------------------------

def test_list_endorsements_empty_when_none(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    result = list_endorsements(path, pw, "alpha")
    assert result == {}


def test_endorsement_counts_multiple_qualities(tmp_store):
    _seed(tmp_store)
    path, pw = tmp_store
    endorse(path, pw, "alpha", "secure", actor="alice")
    endorse(path, pw, "alpha", "reliable", actor="alice")
    endorse(path, pw, "alpha", "reliable", actor="bob")
    counts = endorsement_counts(path, pw, "alpha")
    assert counts["secure"] == 1
    assert counts["reliable"] == 2
