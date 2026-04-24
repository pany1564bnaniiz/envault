"""CLI tests for reminder commands."""
from __future__ import annotations

import time
from datetime import datetime, timedelta

import pytest
from click.testing import CliRunner

from envault.cli_reminders import cmd_reminder
from envault.storage import save_store


@pytest.fixture()
def store_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, "secret", {"alpha": {"DB": "postgres"}})
    return path


def _invoke(store_file, *args):
    runner = CliRunner(mix_stderr=False)
    return runner.invoke(
        cmd_reminder,
        [*args, "--store", store_file, "--password", "secret"],
        catch_exceptions=False,
    )


def _future_iso():
    return (datetime.now() + timedelta(days=1)).isoformat()


def test_reminder_set_success(store_file):
    result = _invoke(store_file, "set", "alpha", "rotate keys", _future_iso())
    assert result.exit_code == 0
    assert "Reminder set" in result.output


def test_reminder_get_shows_message(store_file):
    _invoke(store_file, "set", "alpha", "check expiry", _future_iso())
    result = _invoke(store_file, "get", "alpha")
    assert result.exit_code == 0
    assert "check expiry" in result.output


def test_reminder_get_unset_shows_none(store_file):
    result = _invoke(store_file, "get", "alpha")
    assert result.exit_code == 0
    assert "No reminder" in result.output


def test_reminder_delete_success(store_file):
    _invoke(store_file, "set", "alpha", "msg", _future_iso())
    result = _invoke(store_file, "delete", "alpha")
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_reminder_list_shows_entries(store_file):
    _invoke(store_file, "set", "alpha", "review creds", _future_iso())
    result = _invoke(store_file, "list")
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "review creds" in result.output


def test_reminder_list_empty(store_file):
    result = _invoke(store_file, "list")
    assert result.exit_code == 0
    assert "No reminders" in result.output


def test_reminder_set_missing_project_exits_nonzero(store_file):
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cmd_reminder,
        ["set", "ghost", "msg", _future_iso(), "--store", store_file, "--password", "secret"],
    )
    assert result.exit_code != 0
