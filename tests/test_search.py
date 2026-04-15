"""Tests for envault.search."""

import pytest

from envault.storage import save_store
from envault.search import search_keys, search_values

PASSWORD = "hunter2"


@pytest.fixture()
def tmp_store(tmp_path, monkeypatch):
    store_file = tmp_path / "store.json.enc"
    monkeypatch.setattr("envault.storage.STORE_PATH", store_file)
    monkeypatch.setattr("envault.search.load_store",
                        lambda pw: _load(pw, store_file))
    return store_file


def _load(password, path):
    """Helper that honours the monkeypatched path."""
    import envault.storage as s
    orig = s.STORE_PATH
    s.STORE_PATH = path
    result = s.load_store(password)
    s.STORE_PATH = orig
    return result


def _seed(store_file):
    import envault.storage as s
    orig = s.STORE_PATH
    s.STORE_PATH = store_file
    s.save_store(
        {
            "alpha": {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"},
            "beta":  {"DB_HOST": "remotehost", "REDIS_URL": "redis://localhost"},
        },
        PASSWORD,
    )
    s.STORE_PATH = orig


def test_search_keys_finds_match(tmp_store):
    _seed(tmp_store)
    results = search_keys(PASSWORD, "DB")
    keys_found = [k for _, k in results]
    assert "DB_HOST" in keys_found
    assert "DB_PORT" in keys_found


def test_search_keys_case_insensitive(tmp_store):
    _seed(tmp_store)
    results = search_keys(PASSWORD, "db_host")
    assert len(results) == 2  # one per project


def test_search_keys_case_sensitive_no_match(tmp_store):
    _seed(tmp_store)
    results = search_keys(PASSWORD, "db_host", case_sensitive=True)
    assert results == []


def test_search_keys_scoped_to_project(tmp_store):
    _seed(tmp_store)
    results = search_keys(PASSWORD, "REDIS", project="beta")
    assert results == [("beta", "REDIS_URL")]


def test_search_keys_unknown_project_returns_empty(tmp_store):
    _seed(tmp_store)
    results = search_keys(PASSWORD, "DB", project="nonexistent")
    assert results == []


def test_search_values_finds_match(tmp_store):
    _seed(tmp_store)
    results = search_values(PASSWORD, "localhost")
    projects = [p for p, _, _ in results]
    assert "alpha" in projects
    assert "beta" in projects


def test_search_values_scoped_to_project(tmp_store):
    _seed(tmp_store)
    results = search_values(PASSWORD, "secret", project="alpha")
    assert len(results) == 1
    assert results[0] == ("alpha", "API_KEY", "secret")


def test_search_values_no_match_returns_empty(tmp_store):
    _seed(tmp_store)
    results = search_values(PASSWORD, "NOMATCH_XYZ")
    assert results == []
