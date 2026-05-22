"""Tests for envault.objectives."""
import pytest

from envault.storage import save_store
from envault.objectives import (
    set_objective,
    get_objective,
    delete_objective,
    list_objectives,
)

PASSWORD = "test-pass"


@pytest.fixture()
def tmp_store(tmp_path):
    return tmp_path / "vault.enc"


def _seed(store_path, project="alpha"):
    store = {project: {"KEY": "value"}}
    save_store(store_path, PASSWORD, store)
    return store_path


def test_set_and_get_objective(tmp_store):
    _seed(tmp_store)
    entry = set_objective(tmp_store, PASSWORD, "alpha", "Launch MVP")
    assert entry["text"] == "Launch MVP"
    fetched = get_objective(tmp_store, PASSWORD, "alpha")
    assert fetched is not None
    assert fetched["text"] == "Launch MVP"


def test_get_objective_returns_none_when_unset(tmp_store):
    _seed(tmp_store)
    result = get_objective(tmp_store, PASSWORD, "alpha")
    assert result is None


def test_set_objective_missing_project_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError, match="ghost"):
        set_objective(tmp_store, PASSWORD, "ghost", "Some goal")


def test_set_objective_with_due(tmp_store):
    _seed(tmp_store)
    entry = set_objective(tmp_store, PASSWORD, "alpha", "Ship v2", due="2025-12-31")
    assert entry["due"] == "2025-12-31"
    fetched = get_objective(tmp_store, PASSWORD, "alpha")
    assert fetched["due"] == "2025-12-31"


def test_set_objective_overwrites_previous(tmp_store):
    _seed(tmp_store)
    set_objective(tmp_store, PASSWORD, "alpha", "Old goal")
    set_objective(tmp_store, PASSWORD, "alpha", "New goal")
    fetched = get_objective(tmp_store, PASSWORD, "alpha")
    assert fetched["text"] == "New goal"


def test_delete_objective_returns_true(tmp_store):
    _seed(tmp_store)
    set_objective(tmp_store, PASSWORD, "alpha", "To remove")
    result = delete_objective(tmp_store, PASSWORD, "alpha")
    assert result is True
    assert get_objective(tmp_store, PASSWORD, "alpha") is None


def test_delete_objective_missing_returns_false(tmp_store):
    _seed(tmp_store)
    result = delete_objective(tmp_store, PASSWORD, "alpha")
    assert result is False


def test_list_objectives_empty(tmp_store):
    _seed(tmp_store)
    assert list_objectives(tmp_store, PASSWORD) == {}


def test_list_objectives_shows_all(tmp_store):
    save_store(tmp_store, PASSWORD, {"alpha": {}, "beta": {}})
    set_objective(tmp_store, PASSWORD, "alpha", "Goal A")
    set_objective(tmp_store, PASSWORD, "beta", "Goal B")
    objectives = list_objectives(tmp_store, PASSWORD)
    assert set(objectives.keys()) == {"alpha", "beta"}
    assert objectives["alpha"]["text"] == "Goal A"
    assert objectives["beta"]["text"] == "Goal B"


def test_objective_entry_has_updated_at(tmp_store):
    _seed(tmp_store)
    entry = set_objective(tmp_store, PASSWORD, "alpha", "Check timestamp")
    assert "updated_at" in entry
