"""Tests for CLI hook commands."""
import pytest
from click.testing import CliRunner
from envault.cli_hooks import cmd_hook
from envault.storage import save_store
from envault.projects import set_env


@pytest.fixture
def store_file(tmp_path):
    path = tmp_path / "store.db"
    save_store(str(path), "secret", {})
    set_env(str(path), "secret", "myproject", "FOO", "bar")
    return str(path)


def _invoke(store_file, *args):
    runner = CliRunner()
    return runner.invoke(
        cmd_hook,
        list(args) + ["--store", store_file, "--password", "secret"],
    )


def test_hook_add_success(store_file):
    result = _invoke(store_file, "add", "myproject", "post_set", "echo done")
    assert result.exit_code == 0
    assert "Hook added" in result.output


def test_hook_list_shows_added(store_file):
    _invoke(store_file, "add", "myproject", "post_set", "echo hello")
    result = _invoke(store_file, "list", "myproject")
    assert result.exit_code == 0
    assert "echo hello" in result.output


def test_hook_list_empty(store_file):
    result = _invoke(store_file, "list", "myproject")
    assert result.exit_code == 0
    assert "No hooks" in result.output


def test_hook_remove_success(store_file):
    _invoke(store_file, "add", "myproject", "pre_set", "echo x")
    result = _invoke(store_file, "remove", "myproject", "pre_set", "0")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_hook_add_invalid_event(store_file):
    result = _invoke(store_file, "add", "myproject", "bad_event", "echo x")
    assert result.exit_code != 0
