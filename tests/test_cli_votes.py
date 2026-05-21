"""CLI tests for envault vote commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_votes import cmd_vote
from envault.projects import set_env


@pytest.fixture()
def store_file(tmp_path):
    p = str(tmp_path / "vault.enc")
    set_env(p, "secret", "myapp", "DB", "postgres")
    return p


def _invoke(store_file, *args):
    runner = CliRunner()
    return runner.invoke(
        cmd_vote,
        [*args, "--store", store_file, "--password", "secret"],
        catch_exceptions=False,
    )


def test_vote_up_success(store_file):
    result = _invoke(store_file, "up", "myapp", "--actor", "alice")
    assert result.exit_code == 0
    assert "Total votes: 1" in result.output


def test_vote_up_idempotent_message(store_file):
    _invoke(store_file, "up", "myapp", "--actor", "alice")
    result = _invoke(store_file, "up", "myapp", "--actor", "alice")
    assert "Total votes: 1" in result.output


def test_vote_down_success(store_file):
    _invoke(store_file, "up", "myapp", "--actor", "alice")
    result = _invoke(store_file, "down", "myapp", "--actor", "alice")
    assert result.exit_code == 0
    assert "Total votes: 0" in result.output


def test_vote_show_output(store_file):
    _invoke(store_file, "up", "myapp", "--actor", "alice")
    runner = CliRunner()
    result = runner.invoke(
        cmd_vote,
        ["show", "myapp", "--store", store_file, "--password", "secret"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Votes: 1" in result.output
    assert "alice" in result.output


def test_vote_top_output(store_file):
    _invoke(store_file, "up", "myapp", "--actor", "alice")
    runner = CliRunner()
    result = runner.invoke(
        cmd_vote,
        ["top", "--store", store_file, "--password", "secret"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "myapp" in result.output


def test_vote_up_missing_project_exits_nonzero(store_file):
    runner = CliRunner()
    result = runner.invoke(
        cmd_vote,
        ["up", "ghost", "--store", store_file, "--password", "secret"],
    )
    assert result.exit_code != 0


def test_vote_top_empty_message(store_file):
    runner = CliRunner()
    result = runner.invoke(
        cmd_vote,
        ["top", "--store", store_file, "--password", "secret"],
        catch_exceptions=False,
    )
    assert "No votes" in result.output
