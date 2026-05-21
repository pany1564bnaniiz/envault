"""CLI tests for complexity commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_complexity import cmd_complexity
from envault.projects import set_env


@pytest.fixture()
def store_file(tmp_path):
    return tmp_path / "vault.enc"


def _invoke(args, store_file, password="pw"):
    runner = CliRunner()
    return runner.invoke(
        cmd_complexity,
        args + ["--password", password, "--store", str(store_file)],
        catch_exceptions=False,
    )


def _seed(store_file, project="myapp", password="pw"):
    set_env(project, "KEY", "val", password, store_path=store_file)


def test_complexity_show_success(store_file):
    _seed(store_file)
    result = _invoke(["show", "myapp"], store_file)
    assert result.exit_code == 0
    assert "Score" in result.output
    assert "myapp" in result.output


def test_complexity_show_breakdown_present(store_file):
    _seed(store_file)
    result = _invoke(["show", "myapp"], store_file)
    assert "key_count" in result.output
    assert "has_tags" in result.output


def test_complexity_show_missing_project_exits_nonzero(store_file):
    _seed(store_file)
    runner = CliRunner()
    result = runner.invoke(
        cmd_complexity,
        ["show", "ghost", "--password", "pw", "--store", str(store_file)],
    )
    assert result.exit_code != 0


def test_complexity_rank_lists_projects(store_file):
    _seed(store_file, "alpha")
    _seed(store_file, "beta")
    result = _invoke(["rank"], store_file)
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_complexity_rank_top_option(store_file):
    for name in ["a", "b", "c"]:
        _seed(store_file, name)
    result = _invoke(["rank", "--top", "1"], store_file)
    assert result.exit_code == 0
    lines = [l for l in result.output.splitlines() if l.strip() and "---" not in l and "Project" not in l]
    assert len(lines) == 1


def test_complexity_rank_empty_store(store_file):
    from envault.storage import save_store
    save_store({}, "pw", path=store_file)
    result = _invoke(["rank"], store_file)
    assert result.exit_code == 0
    assert "No projects" in result.output
