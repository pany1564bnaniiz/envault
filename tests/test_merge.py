"""Tests for envault.merge."""

from __future__ import annotations

import os
import pytest

from envault.merge import merge_projects
from envault.projects import get_all_env, set_env
from envault.storage import load_store, save_store


PASSWORD = "test-secret"


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.db")
    store = {}
    save_store(path, PASSWORD, store)
    return path


def _seed(store_path: str, project: str, env: dict) -> None:
    for k, v in env.items():
        set_env(store_path, PASSWORD, project, k, v)


# ---------------------------------------------------------------------------
# merge_projects – basic behaviour
# ---------------------------------------------------------------------------

def test_merge_adds_new_keys(tmp_store):
    _seed(tmp_store, "src", {"FOO": "foo", "BAR": "bar"})
    _seed(tmp_store, "dst", {})

    result = merge_projects(tmp_store, PASSWORD, "src", "dst")

    assert set(result.added) == {"FOO", "BAR"}
    assert result.skipped == []
    assert result.overwritten == []

    dst_env = get_all_env(tmp_store, PASSWORD, "dst")
    assert dst_env["FOO"] == "foo"
    assert dst_env["BAR"] == "bar"


def test_merge_keep_strategy_preserves_destination(tmp_store):
    _seed(tmp_store, "src", {"KEY": "from_src"})
    _seed(tmp_store, "dst", {"KEY": "from_dst"})

    result = merge_projects(tmp_store, PASSWORD, "src", "dst", conflict="keep")

    assert "KEY" in result.skipped
    assert get_all_env(tmp_store, PASSWORD, "dst")["KEY"] == "from_dst"


def test_merge_overwrite_strategy_replaces_destination(tmp_store):
    _seed(tmp_store, "src", {"KEY": "new_value"})
    _seed(tmp_store, "dst", {"KEY": "old_value"})

    result = merge_projects(tmp_store, PASSWORD, "src", "dst", conflict="overwrite")

    assert "KEY" in result.overwritten
    assert get_all_env(tmp_store, PASSWORD, "dst")["KEY"] == "new_value"


def test_merge_mixed_keys(tmp_store):
    _seed(tmp_store, "src", {"NEW": "n", "SHARED": "src_val"})
    _seed(tmp_store, "dst", {"SHARED": "dst_val", "EXISTING": "e"})

    result = merge_projects(tmp_store, PASSWORD, "src", "dst", conflict="keep")

    assert result.added == ["NEW"]
    assert result.skipped == ["SHARED"]
    dst_env = get_all_env(tmp_store, PASSWORD, "dst")
    assert dst_env["SHARED"] == "dst_val"
    assert dst_env["NEW"] == "n"


def test_merge_source_not_found_raises(tmp_store):
    _seed(tmp_store, "dst", {"A": "1"})
    with pytest.raises(KeyError, match="missing_src"):
        merge_projects(tmp_store, PASSWORD, "missing_src", "dst")


def test_merge_destination_not_found_raises(tmp_store):
    _seed(tmp_store, "src", {"A": "1"})
    with pytest.raises(KeyError, match="missing_dst"):
        merge_projects(tmp_store, PASSWORD, "src", "missing_dst")


def test_merge_same_project_raises(tmp_store):
    _seed(tmp_store, "proj", {"A": "1"})
    with pytest.raises(ValueError, match="different"):
        merge_projects(tmp_store, PASSWORD, "proj", "proj")


def test_merge_source_unchanged(tmp_store):
    _seed(tmp_store, "src", {"X": "x"})
    _seed(tmp_store, "dst", {})

    merge_projects(tmp_store, PASSWORD, "src", "dst")

    assert get_all_env(tmp_store, PASSWORD, "src") == {"X": "x"}
