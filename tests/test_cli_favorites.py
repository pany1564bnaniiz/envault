"""Tests for the favorites CLI commands."""

import pytest
from click.testing import CliRunner
from envault.cli_favorites import register_favorites_commands
import click
import os


@pytest.fixture
def store_file(tmp_path):
    return str(tmp_path / "vault.db")


@pytest.fixture
def _invoke(store_file):
    @click.group()
    def root():
        pass

    register_favorites_commands(root)

    runner = CliRunner()

    def invoke(*args):
        return runner.invoke(root, ["--store", store_file, "--password", "secret"] + list(args))

    # Seed a project so favorites have something to reference
    from envault.projects import set_env
    set_env(store_file, "secret", "myproject", "KEY", "val")

    return invoke


def _invoke_factory(store_file):
    """Return a runner that seeds a project and exposes the favorites commands."""
    from envault.projects import set_env
    set_env(store_file, "secret", "myproject", "KEY", "val")

    @click.group()
    def root():
        pass

    register_favorites_commands(root)
    runner = CliRunner()

    def invoke(*args):
        return runner.invoke(root, ["--store", store_file, "--password", "secret"] + list(args))

    return invoke


def test_fav_add_success(store_file):
    invoke = _invoke_factory(store_file)
    result = invoke("fav", "add", "myproject")
    assert result.exit_code == 0
    assert "myproject" in result.output


def test_fav_list_shows_added(store_file):
    invoke = _invoke_factory(store_file)
    invoke("fav", "add", "myproject")
    result = invoke("fav", "list")
    assert result.exit_code == 0
    assert "myproject" in result.output


def test_fav_list_empty(store_file):
    invoke = _invoke_factory(store_file)
    result = invoke("fav", "list")
    assert result.exit_code == 0
    assert "No favorites" in result.output or result.output.strip() == ""


def test_fav_remove_success(store_file):
    invoke = _invoke_factory(store_file)
    invoke("fav", "add", "myproject")
    result = invoke("fav", "remove", "myproject")
    assert result.exit_code == 0
    list_result = invoke("fav", "list")
    assert "myproject" not in list_result.output


def test_fav_add_missing_project_exits_nonzero(store_file):
    invoke = _invoke_factory(store_file)
    result = invoke("fav", "add", "ghost_project")
    assert result.exit_code != 0
