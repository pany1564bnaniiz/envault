"""CLI integration tests for the changelog feature."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
import click

from envault.storage import save_store
from envault.cli_changelog import register_changelog_commands


@pytest.fixture()
def store_file(tmp_path):
    path = tmp_path / "vault.enc"
    save_store(path, "secret", {"proj": {"K": "V"}})
    return path


def _invoke(store_file):
    @click.group()
    def root():
        pass

    register_changelog_commands(root, store_file, lambda: "secret")
    runner = CliRunner()

    def invoke(*args):
        return runner.invoke(root, list(args))

    return invoke


def test_changelog_add_success(store_file):
    invoke = _invoke(store_file)
    result = invoke("changelog", "add", "proj", "Initial commit")
    assert result.exit_code == 0
    assert "Initial commit" in result.output


def test_changelog_add_includes_author(store_file):
    invoke = _invoke(store_file)
    result = invoke("changelog", "add", "proj", "Deploy", "--author", "bob")
    assert result.exit_code == 0
    assert "bob" in result.output


def test_changelog_show_empty(store_file):
    invoke = _invoke(store_file)
    result = invoke("changelog", "show", "proj")
    assert result.exit_code == 0
    assert "No changelog" in result.output


def test_changelog_show_after_add(store_file):
    invoke = _invoke(store_file)
    invoke("changelog", "add", "proj", "Feature X")
    result = invoke("changelog", "show", "proj")
    assert "Feature X" in result.output


def test_changelog_clear_success(store_file):
    invoke = _invoke(store_file)
    invoke("changelog", "add", "proj", "entry")
    result = invoke("changelog", "clear", "proj")
    assert result.exit_code == 0
    assert "1" in result.output


def test_changelog_add_missing_project_exits_nonzero(store_file):
    invoke = _invoke(store_file)
    result = invoke("changelog", "add", "ghost", "msg")
    assert result.exit_code != 0
