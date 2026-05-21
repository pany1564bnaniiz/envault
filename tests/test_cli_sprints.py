"""CLI tests for sprint commands."""
import pytest
from click.testing import CliRunner

from envault.cli_sprints import cmd_sprint
from envault.storage import save_store

PASS = "testpass"


@pytest.fixture()
def store_file(tmp_path):
    path = tmp_path / "vault.enc"
    save_store(path, PASS, {"alpha": {"K": "V"}})
    return path


def _invoke(store_file, *args):
    runner = CliRunner()
    base = ["--store", str(store_file), "--password", PASS]
    return runner.invoke(cmd_sprint, list(args) + base)


def test_sprint_set_success(store_file):
    result = _invoke(store_file, "set", "alpha", "Sprint 1", "2024-01-01", "2024-01-14")
    assert result.exit_code == 0
    assert "Sprint 1" in result.output
    assert "alpha" in result.output


def test_sprint_get_shows_entry(store_file):
    _invoke(store_file, "set", "alpha", "Sprint 1", "2024-01-01", "2024-01-14")
    result = _invoke(store_file, "get", "alpha")
    assert result.exit_code == 0
    assert "Sprint 1" in result.output


def test_sprint_get_unset_project(store_file):
    result = _invoke(store_file, "get", "alpha")
    assert result.exit_code == 0
    assert "No sprint" in result.output


def test_sprint_delete_success(store_file):
    _invoke(store_file, "set", "alpha", "Sprint 1", "2024-01-01", "2024-01-14")
    result = _invoke(store_file, "delete", "alpha")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_sprint_delete_absent(store_file):
    result = _invoke(store_file, "delete", "alpha")
    assert result.exit_code == 0
    assert "No sprint found" in result.output


def test_sprint_list_empty(store_file):
    result = _invoke(store_file, "list")
    assert result.exit_code == 0
    assert "No sprints" in result.output


def test_sprint_list_shows_entry(store_file):
    _invoke(store_file, "set", "alpha", "Sprint 1", "2024-01-01", "2024-01-14")
    result = _invoke(store_file, "list")
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "Sprint 1" in result.output


def test_sprint_set_missing_project_exits_nonzero(store_file):
    result = _invoke(store_file, "set", "ghost", "S1", "2024-01-01", "2024-01-07")
    assert result.exit_code != 0


def test_sprint_active_shows_current(store_file):
    _invoke(store_file, "set", "alpha", "S1", "2024-01-01", "2024-12-31")
    result = _invoke(store_file, "active", "--as-of", "2024-06-15")
    assert result.exit_code == 0
    assert "alpha" in result.output
