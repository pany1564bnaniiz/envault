"""Tests for envault.cli_status CLI commands."""

import pytest
from click.testing import CliRunner

from envault.cli_status import cmd_status
from envault.projects import set_env

PASSWORD = "testpass"


@pytest.fixture()
def store_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    set_env(path, PASSWORD, "myproject", "FOO", "bar")
    return path


def _invoke(store_file, *args):
    runner = CliRunner()
    return runner.invoke(
        cmd_status,
        list(args) + ["--store", store_file, "--password", PASSWORD],
        catch_exceptions=False,
    )


def test_status_set_success(store_file):
    result = _invoke(store_file, "set", "myproject", "active")
    assert result.exit_code == 0
    assert "active" in result.output


def test_status_get_shows_entry(store_file):
    _invoke(store_file, "set", "myproject", "stable", "--note", "looks good")
    result = _invoke(store_file, "get", "myproject")
    assert result.exit_code == 0
    assert "stable" in result.output
    assert "looks good" in result.output


def test_status_get_unset_project(store_file):
    result = _invoke(store_file, "get", "myproject")
    assert result.exit_code == 0
    assert "No status" in result.output


def test_status_remove_success(store_file):
    _invoke(store_file, "set", "myproject", "inactive")
    result = _invoke(store_file, "remove", "myproject")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_status_remove_not_set(store_file):
    result = _invoke(store_file, "remove", "myproject")
    assert result.exit_code == 0
    assert "No status found" in result.output


def test_status_list_empty(store_file):
    result = _invoke(store_file, "list")
    assert result.exit_code == 0
    assert "No statuses" in result.output


def test_status_list_shows_entry(store_file):
    _invoke(store_file, "set", "myproject", "experimental")
    result = _invoke(store_file, "list")
    assert result.exit_code == 0
    assert "myproject" in result.output
    assert "experimental" in result.output


def test_status_set_missing_project_exits_nonzero(store_file):
    runner = CliRunner()
    result = runner.invoke(
        cmd_status,
        ["set", "ghost", "active", "--store", store_file, "--password", PASSWORD],
    )
    assert result.exit_code != 0
