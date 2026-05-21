"""Tests for envault.complexity."""

from __future__ import annotations

import pytest

from envault.complexity import compute_complexity, rank_projects, WEIGHTS
from envault.storage import load_store, save_store


@pytest.fixture()
def tmp_store(tmp_path):
    return tmp_path / "vault.enc"


def _seed(store_path, password, project, keys=None):
    from envault.projects import set_env
    for k, v in (keys or {"KEY": "val"}).items():
        set_env(project, k, v, password, store_path=store_path)


def test_compute_complexity_returns_score(tmp_store):
    _seed(tmp_store, "pw", "alpha")
    result = compute_complexity("alpha", "pw", store_path=tmp_store)
    assert result["project"] == "alpha"
    assert isinstance(result["score"], int)
    assert result["score"] >= 1


def test_compute_complexity_key_count_in_breakdown(tmp_store):
    _seed(tmp_store, "pw", "alpha", {"A": "1", "B": "2", "C": "3"})
    result = compute_complexity("alpha", "pw", store_path=tmp_store)
    assert result["breakdown"]["key_count"] == 3


def test_compute_complexity_missing_project_raises(tmp_store):
    _seed(tmp_store, "pw", "alpha")
    with pytest.raises(KeyError, match="beta"):
        compute_complexity("beta", "pw", store_path=tmp_store)


def test_compute_complexity_no_metadata_flags_false(tmp_store):
    _seed(tmp_store, "pw", "plain")
    result = compute_complexity("plain", "pw", store_path=tmp_store)
    bd = result["breakdown"]
    assert bd["has_tags"] is False
    assert bd["has_notes"] is False
    assert bd["has_hooks"] is False


def test_compute_complexity_with_tags_raises_score(tmp_store):
    _seed(tmp_store, "pw", "tagged")
    store = load_store("pw", path=tmp_store)
    store["tagged"]["__tags__"] = ["production"]
    save_store(store, "pw", path=tmp_store)

    result = compute_complexity("tagged", "pw", store_path=tmp_store)
    assert result["breakdown"]["has_tags"] is True
    assert result["score"] >= WEIGHTS["has_tags"]


def test_rank_projects_sorted_descending(tmp_store):
    _seed(tmp_store, "pw", "simple", {"X": "1"})
    _seed(tmp_store, "pw", "complex", {"A": "1", "B": "2", "C": "3"})

    store = load_store("pw", path=tmp_store)
    store["complex"]["__tags__"] = ["prod"]
    store["complex"]["__hooks__"] = {"post_set": ["echo hi"]}
    save_store(store, "pw", path=tmp_store)

    ranked = rank_projects("pw", store_path=tmp_store)
    assert ranked[0]["project"] == "complex"
    assert ranked[0]["score"] > ranked[-1]["score"]


def test_rank_projects_empty_store(tmp_store):
    # no projects seeded — should return empty list without error
    from envault.storage import save_store
    save_store({}, "pw", path=tmp_store)
    assert rank_projects("pw", store_path=tmp_store) == []
