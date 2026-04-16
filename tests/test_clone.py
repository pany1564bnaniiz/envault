"""Tests for envault.clone."""

import pytest
from pathlib import Path

from envault.storage import load_store, save_store
from envault.projects import set_env, get_env, get_all_env
from envault.clone import clone_project

PASSWORD = "clonepass"


@pytest.fixture()
def tmp_store(tmp_path):
    return tmp_path / "store.enc"


def _seed(tmp_store):
    set_env(tmp_store, PASSWORD, "alpha", "KEY1", "val1")
    set_env(tmp_store, PASSWORD, "alpha", "KEY2", "val2")


def test_clone_returns_key_count(tmp_store):
    _seed(tmp_store)
    count = clone_project(tmp_store, PASSWORD, "alpha", "beta")
    assert count == 2


def test_clone_copies_all_keys(tmp_store):
    _seed(tmp_store)
    clone_project(tmp_store, PASSWORD, "alpha", "beta")
    assert get_env(tmp_store, PASSWORD, "beta", "KEY1") == "val1"
    assert get_env(tmp_store, PASSWORD, "beta", "KEY2") == "val2"


def test_clone_does_not_mutate_source(tmp_store):
    _seed(tmp_store)
    clone_project(tmp_store, PASSWORD, "alpha", "beta")
    assert get_all_env(tmp_store, PASSWORD, "alpha") == {"KEY1": "val1", "KEY2": "val2"}


def test_clone_missing_src_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        clone_project(tmp_store, PASSWORD, "ghost", "beta")


def test_clone_existing_dst_raises_without_overwrite(tmp_store):
    _seed(tmp_store)
    set_env(tmp_store, PASSWORD, "beta", "OTHER", "x")
    with pytest.raises(ValueError, match="already exists"):
        clone_project(tmp_store, PASSWORD, "alpha", "beta")


def test_clone_existing_dst_overwrite(tmp_store):
    _seed(tmp_store)
    set_env(tmp_store, PASSWORD, "beta", "OLD", "old_val")
    clone_project(tmp_store, PASSWORD, "alpha", "beta", overwrite=True)
    env = get_all_env(tmp_store, PASSWORD, "beta")
    assert env.get("KEY1") == "val1"
    assert env.get("KEY2") == "val2"
