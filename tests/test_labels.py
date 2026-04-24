"""Tests for envault.labels."""
from __future__ import annotations

import pytest

from envault.labels import (
    VALID_COLOURS,
    get_label,
    list_labels,
    projects_by_colour,
    remove_label,
    set_label,
)
from envault.projects import set_env
from envault.storage import load_store, save_store


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, "pw", {})
    return path


def _seed(store_path: str, project: str) -> None:
    set_env(store_path, "pw", project, "KEY", "val")


# ---------------------------------------------------------------------------
# set_label / get_label
# ---------------------------------------------------------------------------

def test_set_and_get_label(tmp_store):
    _seed(tmp_store, "alpha")
    set_label(tmp_store, "pw", "alpha", "red")
    assert get_label(tmp_store, "pw", "alpha") == "red"


def test_get_label_returns_none_when_unset(tmp_store):
    _seed(tmp_store, "beta")
    assert get_label(tmp_store, "pw", "beta") is None


def test_set_label_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        set_label(tmp_store, "pw", "ghost", "blue")


def test_set_label_invalid_colour_raises(tmp_store):
    _seed(tmp_store, "gamma")
    with pytest.raises(ValueError, match="Invalid colour"):
        set_label(tmp_store, "pw", "gamma", "ultraviolet")


def test_set_label_overwrites_previous(tmp_store):
    _seed(tmp_store, "delta")
    set_label(tmp_store, "pw", "delta", "green")
    set_label(tmp_store, "pw", "delta", "yellow")
    assert get_label(tmp_store, "pw", "delta") == "yellow"


# ---------------------------------------------------------------------------
# remove_label
# ---------------------------------------------------------------------------

def test_remove_label(tmp_store):
    _seed(tmp_store, "epsilon")
    set_label(tmp_store, "pw", "epsilon", "cyan")
    remove_label(tmp_store, "pw", "epsilon")
    assert get_label(tmp_store, "pw", "epsilon") is None


def test_remove_label_noop_when_unset(tmp_store):
    _seed(tmp_store, "zeta")
    remove_label(tmp_store, "pw", "zeta")  # should not raise


# ---------------------------------------------------------------------------
# list_labels
# ---------------------------------------------------------------------------

def test_list_labels_empty_when_none(tmp_store):
    assert list_labels(tmp_store, "pw") == {}


def test_list_labels_returns_all(tmp_store):
    for name, colour in [("p1", "red"), ("p2", "blue"), ("p3", "red")]:
        _seed(tmp_store, name)
        set_label(tmp_store, "pw", name, colour)
    mapping = list_labels(tmp_store, "pw")
    assert mapping == {"p1": "red", "p2": "blue", "p3": "red"}


# ---------------------------------------------------------------------------
# projects_by_colour
# ---------------------------------------------------------------------------

def test_projects_by_colour(tmp_store):
    for name, colour in [("a", "magenta"), ("b", "magenta"), ("c", "grey")]:
        _seed(tmp_store, name)
        set_label(tmp_store, "pw", name, colour)
    result = projects_by_colour(tmp_store, "pw", "magenta")
    assert result == ["a", "b"]


def test_projects_by_colour_empty_when_none_match(tmp_store):
    _seed(tmp_store, "solo")
    set_label(tmp_store, "pw", "solo", "white")
    assert projects_by_colour(tmp_store, "pw", "blue") == []


# ---------------------------------------------------------------------------
# isolation: labels key must not appear in list_projects
# ---------------------------------------------------------------------------

def test_labels_key_not_in_list_projects(tmp_store):
    from envault.storage import list_projects
    _seed(tmp_store, "visible")
    set_label(tmp_store, "pw", "visible", "green")
    projects = list_projects(tmp_store, "pw")
    assert "__labels__" not in projects
    assert "visible" in projects
