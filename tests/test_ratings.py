"""Tests for envault.ratings."""

from __future__ import annotations

import pytest

from envault.ratings import (
    average_score,
    delete_rating,
    get_rating,
    list_ratings,
    set_rating,
)
from envault.storage import save_store

PASSWORD = "testpass"


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, PASSWORD, {"alpha": {"KEY": "val"}, "beta": {"X": "1"}})
    return path


def _seed(tmp_store):
    set_rating(tmp_store, PASSWORD, "alpha", 4, "solid")


# ---------------------------------------------------------------------------
# set_rating
# ---------------------------------------------------------------------------

def test_set_rating_persists(tmp_store):
    set_rating(tmp_store, PASSWORD, "alpha", 5, "excellent")
    r = get_rating(tmp_store, PASSWORD, "alpha")
    assert r is not None
    assert r["score"] == 5
    assert r["comment"] == "excellent"
    assert "updated_at" in r


def test_set_rating_no_comment(tmp_store):
    set_rating(tmp_store, PASSWORD, "alpha", 3)
    r = get_rating(tmp_store, PASSWORD, "alpha")
    assert r["comment"] == ""


def test_set_rating_invalid_score_raises(tmp_store):
    with pytest.raises(ValueError, match="Score must be between"):
        set_rating(tmp_store, PASSWORD, "alpha", 6)


def test_set_rating_score_zero_raises(tmp_store):
    with pytest.raises(ValueError):
        set_rating(tmp_store, PASSWORD, "alpha", 0)


def test_set_rating_missing_project_raises(tmp_store):
    with pytest.raises(KeyError):
        set_rating(tmp_store, PASSWORD, "nonexistent", 3)


def test_set_rating_overwrites_previous(tmp_store):
    set_rating(tmp_store, PASSWORD, "alpha", 2)
    set_rating(tmp_store, PASSWORD, "alpha", 5, "updated")
    r = get_rating(tmp_store, PASSWORD, "alpha")
    assert r["score"] == 5
    assert r["comment"] == "updated"


# ---------------------------------------------------------------------------
# get_rating
# ---------------------------------------------------------------------------

def test_get_rating_returns_none_when_unset(tmp_store):
    assert get_rating(tmp_store, PASSWORD, "alpha") is None


# ---------------------------------------------------------------------------
# delete_rating
# ---------------------------------------------------------------------------

def test_delete_rating_returns_true_when_exists(tmp_store):
    _seed(tmp_store)
    assert delete_rating(tmp_store, PASSWORD, "alpha") is True
    assert get_rating(tmp_store, PASSWORD, "alpha") is None


def test_delete_rating_returns_false_when_missing(tmp_store):
    assert delete_rating(tmp_store, PASSWORD, "alpha") is False


# ---------------------------------------------------------------------------
# list_ratings / average_score
# ---------------------------------------------------------------------------

def test_list_ratings_sorted_by_score_descending(tmp_store):
    set_rating(tmp_store, PASSWORD, "alpha", 2)
    set_rating(tmp_store, PASSWORD, "beta", 5)
    ratings = list_ratings(tmp_store, PASSWORD)
    keys = list(ratings.keys())
    assert keys[0] == "beta"
    assert keys[1] == "alpha"


def test_list_ratings_empty_when_none(tmp_store):
    assert list_ratings(tmp_store, PASSWORD) == {}


def test_average_score_correct(tmp_store):
    set_rating(tmp_store, PASSWORD, "alpha", 4)
    set_rating(tmp_store, PASSWORD, "beta", 2)
    assert average_score(tmp_store, PASSWORD) == pytest.approx(3.0)


def test_average_score_none_when_no_ratings(tmp_store):
    assert average_score(tmp_store, PASSWORD) is None
