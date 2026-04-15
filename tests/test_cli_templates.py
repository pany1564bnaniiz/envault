"""CLI integration tests for template commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_templates import cmd_template
from envault.templates import save_template, load_template
from envault.projects import get_env


@pytest.fixture()
def store_file(tmp_path):
    return str(tmp_path / "store.enc")


PASSWORD = "cli-test-pass"


def _invoke(args, store, password=PASSWORD):
    runner = CliRunner()
    env = {"ENVAULT_STORE": store, "ENVAULT_PASSWORD": password}
    return runner.invoke(cmd_template, args, env=env, catch_exceptions=False)


def test_template_save_success(store_file):
    result = _invoke(["save", "defaults", "--set", "PORT=8080", "--set", "DEBUG=false"], store_file)
    assert result.exit_code == 0
    assert "defaults" in result.output
    assert "2 key(s)" in result.output


def test_template_list_shows_saved(store_file):
    _invoke(["save", "alpha", "--set", "A=1"], store_file)
    _invoke(["save", "beta", "--set", "B=2"], store_file)
    result = _invoke(["list"], store_file)
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_template_list_empty(store_file):
    result = _invoke(["list"], store_file)
    assert result.exit_code == 0
    assert "No templates" in result.output


def test_template_delete_success(store_file):
    _invoke(["save", "to-del", "--set", "X=1"], store_file)
    result = _invoke(["delete", "to-del"], store_file)
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_template_delete_nonexistent_exits_nonzero(store_file):
    runner = CliRunner()
    env = {"ENVAULT_STORE": store_file, "ENVAULT_PASSWORD": PASSWORD}
    result = runner.invoke(cmd_template, ["delete", "ghost"], env=env)
    assert result.exit_code != 0


def test_template_apply_writes_keys(store_file):
    _invoke(["save", "base", "--set", "HOST=localhost", "--set", "PORT=5432"], store_file)
    result = _invoke(["apply", "base", "myproject"], store_file)
    assert result.exit_code == 0
    assert "2 key(s)" in result.output
    assert get_env(store_file, PASSWORD, "myproject", "HOST") == "localhost"


def test_template_apply_nonexistent_exits_nonzero(store_file):
    runner = CliRunner()
    env = {"ENVAULT_STORE": store_file, "ENVAULT_PASSWORD": PASSWORD}
    result = runner.invoke(cmd_template, ["apply", "ghost", "proj"], env=env)
    assert result.exit_code != 0
