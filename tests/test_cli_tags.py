"""Integration tests for the tag CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_tags import cmd_tag
from envault.storage import save_store


@pytest.fixture()
def store_file(tmp_path):
    path = str(tmp_path / "store.enc")
    store = {
        "myproject": {"KEY": "value"},
        "other": {"X": "1"},
    }
    save_store(path, "secret", store)
    return path


def _invoke(args, store, password="secret"):
    runner = CliRunner()
    return runner.invoke(
        cmd_tag,
        args + ["--store", store, "--password", password],
        catch_exceptions=False,
    )


def test_tag_add_success(store_file):
    result = _invoke(["add", "myproject", "prod"], store_file)
    assert result.exit_code == 0
    assert "prod" in result.output


def test_tag_list_shows_added_tag(store_file):
    _invoke(["add", "myproject", "staging"], store_file)
    result = _invoke(["list", "myproject"], store_file)
    assert result.exit_code == 0
    assert "staging" in result.output


def test_tag_remove_success(store_file):
    _invoke(["add", "myproject", "temp"], store_file)
    result = _invoke(["remove", "myproject", "temp"], store_file)
    assert result.exit_code == 0
    assert "temp" in result.output


def test_tag_find_returns_project(store_file):
    _invoke(["add", "myproject", "backend"], store_file)
    result = _invoke(["find", "backend"], store_file)
    assert result.exit_code == 0
    assert "myproject" in result.output


def test_tag_add_missing_project_exits_nonzero(store_file):
    runner = CliRunner()
    result = runner.invoke(
        cmd_tag,
        ["add", "ghost", "prod", "--store", store_file, "--password", "secret"],
    )
    assert result.exit_code != 0


def test_tag_list_empty_message(store_file):
    result = _invoke(["list", "other"], store_file)
    assert result.exit_code == 0
    assert "No tags" in result.output
