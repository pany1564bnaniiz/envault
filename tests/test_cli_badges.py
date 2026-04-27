"""CLI tests for badge commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_badges import cmd_badge
from envault.storage import save_store


@pytest.fixture()
def store_file(tmp_path):
    path = str(tmp_path / "vault.db")
    save_store(path, "secret", {"myproject": {"FOO": "bar"}})
    return path


def _invoke(args, store, password="secret"):
    runner = CliRunner()
    return runner.invoke(
        cmd_badge,
        ["--store", store, "--password", password] + args
        if args[0] not in ("valid",)
        else args,
    )


def _invoke_cmd(store, password, *args):
    runner = CliRunner()
    full_args = list(args)
    # Inject --store and --password after the sub-command name
    sub = full_args[0]
    rest = full_args[1:]
    return runner.invoke(
        cmd_badge,
        [sub, "--store", store, "--password", password] + rest,
    )


def test_badge_add_success(store_file):
    result = _invoke_cmd(store_file, "secret", "add", "myproject", "production")
    assert result.exit_code == 0
    assert "added" in result.output


def test_badge_list_shows_added(store_file):
    _invoke_cmd(store_file, "secret", "add", "myproject", "stable")
    result = _invoke_cmd(store_file, "secret", "list", "myproject")
    assert result.exit_code == 0
    assert "stable" in result.output


def test_badge_remove_success(store_file):
    _invoke_cmd(store_file, "secret", "add", "myproject", "staging")
    result = _invoke_cmd(store_file, "secret", "remove", "myproject", "staging")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_badge_list_empty(store_file):
    result = _invoke_cmd(store_file, "secret", "list", "myproject")
    assert result.exit_code == 0
    assert "No badges" in result.output


def test_badge_add_invalid_badge_exits_nonzero(store_file):
    result = _invoke_cmd(store_file, "secret", "add", "myproject", "legendary")
    assert result.exit_code != 0


def test_badge_find(store_file):
    _invoke_cmd(store_file, "secret", "add", "myproject", "experimental")
    result = _invoke_cmd(store_file, "secret", "find", "experimental")
    assert result.exit_code == 0
    assert "myproject" in result.output


def test_badge_valid_lists_all():
    runner = CliRunner()
    result = runner.invoke(cmd_badge, ["valid"])
    assert result.exit_code == 0
    assert "production" in result.output
    assert "deprecated" in result.output
