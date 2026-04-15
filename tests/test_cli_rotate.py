"""Integration tests for the *rotate* CLI sub-command."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_rotate import cmd_rotate
from envault.storage import load_store, save_store


@pytest.fixture()
def store_file(tmp_path):
    path = str(tmp_path / "store.enc")
    save_store(path, "old-pass", {"proj": {"FOO": "bar"}})
    return path


def _invoke(store_file, old_pw="old-pass", new_pw="new-pass", confirm_pw=None):
    runner = CliRunner()
    confirm_pw = confirm_pw if confirm_pw is not None else new_pw
    return runner.invoke(
        cmd_rotate,
        [
            "--store", store_file,
            "--old-password", old_pw,
            "--new-password", new_pw,
        ],
        input=f"{new_pw}\n{confirm_pw}\n",
        catch_exceptions=False,
    )


def test_rotate_success_message(store_file):
    result = _invoke(store_file)
    assert result.exit_code == 0
    assert "rotated" in result.output.lower()


def test_rotate_data_accessible_after_rotation(store_file):
    _invoke(store_file)
    data = load_store(store_file, "new-pass")
    assert data["proj"]["FOO"] == "bar"


def test_rotate_wrong_old_password_exits_nonzero(store_file):
    result = _invoke(store_file, old_pw="wrong")
    assert result.exit_code != 0


def test_rotate_empty_new_password_exits_nonzero(store_file):
    runner = CliRunner()
    result = runner.invoke(
        cmd_rotate,
        ["--store", store_file, "--old-password", "old-pass", "--new-password", ""],
        catch_exceptions=False,
    )
    assert result.exit_code != 0
