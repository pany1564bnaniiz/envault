"""Tests for envault.hooks."""
import pytest
from envault.storage import save_store, load_store
from envault.hooks import add_hook, remove_hook, list_hooks, HOOK_EVENTS
from envault.projects import set_env


@pytest.fixture
def tmp_store(tmp_path):
    path = tmp_path / "store.db"
    save_store(str(path), "pass", {})
    store = {"_path": str(path)}
    set_env(str(path), "pass", "proj1", "KEY", "val")
    return store


def test_add_hook_persists(tmp_store):
    add_hook(tmp_store, "pass", "proj1", "post_set", "echo done")
    hooks = list_hooks(tmp_store, "pass", "proj1")
    assert "post_set" in hooks
    assert "echo done" in hooks["post_set"]


def test_add_multiple_hooks_same_event(tmp_store):
    add_hook(tmp_store, "pass", "proj1", "post_set", "echo first")
    add_hook(tmp_store, "pass", "proj1", "post_set", "echo second")
    hooks = list_hooks(tmp_store, "pass", "proj1")
    assert len(hooks["post_set"]) == 2


def test_add_hook_invalid_event_raises(tmp_store):
    with pytest.raises(ValueError, match="Unknown event"):
        add_hook(tmp_store, "pass", "proj1", "on_magic", "echo hi")


def test_remove_hook(tmp_store):
    add_hook(tmp_store, "pass", "proj1", "pre_set", "echo a")
    add_hook(tmp_store, "pass", "proj1", "pre_set", "echo b")
    remove_hook(tmp_store, "pass", "proj1", "pre_set", 0)
    hooks = list_hooks(tmp_store, "pass", "proj1")
    assert hooks["pre_set"] == ["echo b"]


def test_remove_hook_out_of_range_raises(tmp_store):
    add_hook(tmp_store, "pass", "proj1", "pre_set", "echo a")
    with pytest.raises(IndexError):
        remove_hook(tmp_store, "pass", "proj1", "pre_set", 5)


def test_list_hooks_empty_when_none(tmp_store):
    hooks = list_hooks(tmp_store, "pass", "proj1")
    assert hooks == {}


def test_hooks_isolated_per_project(tmp_store):
    set_env(tmp_store["_path"], "pass", "proj2", "K", "v")
    add_hook(tmp_store, "pass", "proj1", "post_set", "echo proj1")
    hooks2 = list_hooks(tmp_store, "pass", "proj2")
    assert hooks2 == {}


def test_all_hook_events_valid():
    assert "pre_set" in HOOK_EVENTS
    assert "post_export" in HOOK_EVENTS
    assert len(HOOK_EVENTS) == 8
