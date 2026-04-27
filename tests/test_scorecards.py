"""Tests for envault.scorecards."""

from __future__ import annotations

import pytest

from envault.scorecards import (
    delete_metric,
    get_scorecard,
    list_scorecards,
    overall_score,
    set_metric,
)
from envault.storage import save_store

PASS = "hunter2"


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "vault.db")


def _seed(store_path: str, project: str = "alpha") -> None:
    save_store(store_path, PASS, {project: {"KEY": "val"}})


# ---------------------------------------------------------------------------
# set_metric / get_scorecard
# ---------------------------------------------------------------------------

def test_set_and_get_metric(tmp_store):
    _seed(tmp_store)
    set_metric(tmp_store, PASS, "alpha", "completeness", 0.8)
    sc = get_scorecard(tmp_store, PASS, "alpha")
    assert sc["completeness"] == pytest.approx(0.8)


def test_set_multiple_metrics(tmp_store):
    _seed(tmp_store)
    set_metric(tmp_store, PASS, "alpha", "completeness", 0.9)
    set_metric(tmp_store, PASS, "alpha", "security", 0.7)
    sc = get_scorecard(tmp_store, PASS, "alpha")
    assert len(sc) == 2


def test_set_metric_invalid_name_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="Invalid metric"):
        set_metric(tmp_store, PASS, "alpha", "nonexistent", 0.5)


def test_set_metric_out_of_range_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        set_metric(tmp_store, PASS, "alpha", "freshness", 1.5)


def test_set_metric_missing_project_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError):
        set_metric(tmp_store, PASS, "ghost", "security", 0.5)


def test_get_scorecard_empty_when_unset(tmp_store):
    _seed(tmp_store)
    assert get_scorecard(tmp_store, PASS, "alpha") == {}


# ---------------------------------------------------------------------------
# overall_score
# ---------------------------------------------------------------------------

def test_overall_score_none_when_no_metrics(tmp_store):
    _seed(tmp_store)
    assert overall_score(tmp_store, PASS, "alpha") is None


def test_overall_score_mean_of_metrics(tmp_store):
    _seed(tmp_store)
    set_metric(tmp_store, PASS, "alpha", "completeness", 0.8)
    set_metric(tmp_store, PASS, "alpha", "security", 0.6)
    score = overall_score(tmp_store, PASS, "alpha")
    assert score == pytest.approx(0.7)


# ---------------------------------------------------------------------------
# delete_metric
# ---------------------------------------------------------------------------

def test_delete_metric_returns_true_when_found(tmp_store):
    _seed(tmp_store)
    set_metric(tmp_store, PASS, "alpha", "stability", 1.0)
    assert delete_metric(tmp_store, PASS, "alpha", "stability") is True
    assert "stability" not in get_scorecard(tmp_store, PASS, "alpha")


def test_delete_metric_returns_false_when_missing(tmp_store):
    _seed(tmp_store)
    assert delete_metric(tmp_store, PASS, "alpha", "stability") is False


# ---------------------------------------------------------------------------
# list_scorecards
# ---------------------------------------------------------------------------

def test_list_scorecards_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert list_scorecards(tmp_store, PASS) == {}


def test_list_scorecards_shows_projects_with_metrics(tmp_store):
    save_store(tmp_store, PASS, {"alpha": {"K": "v"}, "beta": {"K": "v"}})
    set_metric(tmp_store, PASS, "alpha", "documentation", 0.5)
    cards = list_scorecards(tmp_store, PASS)
    assert "alpha" in cards
    assert "beta" not in cards
