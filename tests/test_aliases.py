"""Tests for envault.aliases."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.storage import save_store
from envault.projects import set_env
from envault.aliases import set_alias, remove_alias, resolve_alias, list_aliases
from envault.cli_aliases import cmd_alias


_PASSWORD = "test-pass"


@pytest.fixture()
def tmp_store(tmp_path):
    store_file = str(tmp_path / "vault.enc")
    # Seed a real project so alias targets exist
    set_env(store_file, _PASSWORD, "myproject", "KEY", "val")
    return store_file


def test_set_alias_persists(tmp_store):
    set_alias(tmp_store, _PASSWORD, "mp", "myproject")
    mapping = list_aliases(tmp_store, _PASSWORD)
    assert mapping["mp"] == "myproject"


def test_set_alias_missing_project_raises(tmp_store):
    with pytest.raises(KeyError, match="ghost"):
        set_alias(tmp_store, _PASSWORD, "g", "ghost")


def test_set_alias_idempotent(tmp_store):
    set_alias(tmp_store, _PASSWORD, "mp", "myproject")
    set_alias(tmp_store, _PASSWORD, "mp", "myproject")
    assert list_aliases(tmp_store, _PASSWORD)["mp"] == "myproject"


def test_remove_alias(tmp_store):
    set_alias(tmp_store, _PASSWORD, "mp", "myproject")
    remove_alias(tmp_store, _PASSWORD, "mp")
    assert "mp" not in list_aliases(tmp_store, _PASSWORD)


def test_remove_alias_missing_raises(tmp_store):
    with pytest.raises(KeyError, match="nope"):
        remove_alias(tmp_store, _PASSWORD, "nope")


def test_resolve_alias_returns_project(tmp_store):
    set_alias(tmp_store, _PASSWORD, "mp", "myproject")
    assert resolve_alias(tmp_store, _PASSWORD, "mp") == "myproject"


def test_resolve_alias_passthrough_when_unknown(tmp_store):
    assert resolve_alias(tmp_store, _PASSWORD, "unknown") == "unknown"


def test_list_aliases_empty_initially(tmp_store):
    assert list_aliases(tmp_store, _PASSWORD) == {}


# --- CLI tests ---

@pytest.fixture()
def store_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    set_env(path, _PASSWORD, "proj1", "A", "1")
    return path


def _invoke(args, store_file):
    runner = CliRunner()
    env = {"ENVAULT_STORE": store_file, "ENVAULT_PASSWORD": _PASSWORD}
    return runner.invoke(cmd_alias, args, env=env, catch_exceptions=False)


def test_cli_alias_set_success(store_file):
    result = _invoke(["set", "p1", "proj1"], store_file)
    assert result.exit_code == 0
    assert "p1" in result.output


def test_cli_alias_list_shows_alias(store_file):
    _invoke(["set", "p1", "proj1"], store_file)
    result = _invoke(["list"], store_file)
    assert "p1 -> proj1" in result.output


def test_cli_alias_remove_success(store_file):
    _invoke(["set", "p1", "proj1"], store_file)
    result = _invoke(["remove", "p1"], store_file)
    assert result.exit_code == 0
    assert "removed" in result.output
