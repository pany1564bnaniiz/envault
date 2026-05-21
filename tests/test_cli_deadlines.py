"""CLI tests for deadline commands."""
import pytest
from click.testing import CliRunner
from datetime import datetime, timedelta, timezone
from pathlib import Path

from envault.cli import cli
from envault.storage import save_store

PASSWORD = "clitest"


@pytest.fixture()
def store_file(tmp_path):
    path = tmp_path / "vault.enc"
    store = {"myproject": {"DB_URL": "sqlite:///dev.db"}}
    save_store(path, PASSWORD, store)
    return path


def _invoke(store_file, *args):
    runner = CliRunner()
    return runner.invoke(
        cli,
        ["--store", str(store_file), "--password", PASSWORD, *args],
        catch_exceptions=False,
    )


def _future_iso(days=1):
    dt = datetime.now(tz=timezone.utc) + timedelta(days=days)
    return dt.isoformat()


def test_deadline_set_success(store_file):
    result = _invoke(store_file, "deadline", "set", "myproject", _future_iso(), "--label", "v1")
    assert result.exit_code == 0
    assert "myproject" in result.output


def test_deadline_get_shows_due(store_file):
    due = _future_iso(5)
    _invoke(store_file, "deadline", "set", "myproject", due)
    result = _invoke(store_file, "deadline", "get", "myproject")
    assert result.exit_code == 0
    assert "myproject" in result.output


def test_deadline_get_unset(store_file):
    result = _invoke(store_file, "deadline", "get", "myproject")
    assert result.exit_code == 0
    assert "No deadline" in result.output


def test_deadline_delete_success(store_file):
    _invoke(store_file, "deadline", "set", "myproject", _future_iso())
    result = _invoke(store_file, "deadline", "delete", "myproject")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_deadline_list_empty(store_file):
    result = _invoke(store_file, "deadline", "list")
    assert result.exit_code == 0
    assert "No deadlines" in result.output


def test_deadline_set_missing_project_exits_nonzero(store_file):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["--store", str(store_file), "--password", PASSWORD,
         "deadline", "set", "ghost", _future_iso()],
    )
    assert result.exit_code != 0
