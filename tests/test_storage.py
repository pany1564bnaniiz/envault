"""Unit tests for envault.storage encrypted local store."""

import pytest
from pathlib import Path

from envault.storage import load_store, save_store, list_projects

PASSWORD = "test-master-password"


@pytest.fixture
def tmp_store(tmp_path):
    """Provide a temporary directory as the store location."""
    return tmp_path


def test_load_store_empty_when_no_file(tmp_store):
    result = load_store(PASSWORD, store_dir=tmp_store)
    assert result == {}


def test_save_and_load_store(tmp_store):
    data = {
        "my-project": {"API_KEY": "key123", "DEBUG": "true"},
        "other-project": {"TOKEN": "tok456"},
    }
    save_store(data, PASSWORD, store_dir=tmp_store)
    loaded = load_store(PASSWORD, store_dir=tmp_store)
    assert loaded == data


def test_store_file_has_restricted_permissions(tmp_store):
    save_store({"proj": {"X": "1"}}, PASSWORD, store_dir=tmp_store)
    store_file = tmp_store / "store.enc"
    mode = oct(store_file.stat().st_mode)[-3:]
    assert mode == "600"


def test_load_store_wrong_password_raises(tmp_store):
    save_store({"proj": {"A": "1"}}, PASSWORD, store_dir=tmp_store)
    with pytest.raises(Exception):
        load_store("wrong-password", store_dir=tmp_store)


def test_list_projects(tmp_store):
    data = {"beta": {}, "alpha": {}, "gamma": {}}
    save_store(data, PASSWORD, store_dir=tmp_store)
    projects = list_projects(PASSWORD, store_dir=tmp_store)
    assert projects == ["alpha", "beta", "gamma"]


def test_overwrite_store(tmp_store):
    save_store({"proj": {"OLD": "value"}}, PASSWORD, store_dir=tmp_store)
    save_store({"proj": {"NEW": "value"}}, PASSWORD, store_dir=tmp_store)
    loaded = load_store(PASSWORD, store_dir=tmp_store)
    assert loaded == {"proj": {"NEW": "value"}}
