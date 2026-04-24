"""CLI tests for share commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_sharing import cmd_share
from envault.projects import set_env, get_env
from envault.sharing import export_bundle


@pytest.fixture()
def store_file(tmp_path):
    return tmp_path / "store"


def _invoke(store_file, args, input_text=""):
    runner = CliRunner(mix_stderr=False)
    return runner.invoke(cmd_share, args, input=input_text, catch_exceptions=False)


def test_export_prints_bundle(store_file):
    set_env(store_file, "pw", "proj", "KEY", "val")
    result = _invoke(store_file, ["export", "proj", "--store", str(store_file),
                                   "--password", "pw", "--bundle-password", "bpw"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 10


def test_import_success_message(store_file):
    set_env(store_file, "pw", "src", "K", "v")
    bundle = export_bundle(store_file, "pw", "src", "bpw")
    result = _invoke(store_file, ["import", "dest", bundle, "--store", str(store_file),
                                   "--password", "pw", "--bundle-password", "bpw"])
    assert result.exit_code == 0
    assert "1" in result.output


def test_import_wrong_bundle_password_exits_nonzero(store_file):
    set_env(store_file, "pw", "src", "K", "v")
    bundle = export_bundle(store_file, "pw", "src", "bpw")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cmd_share, ["import", "dest", bundle, "--store", str(store_file),
                                       "--password", "pw", "--bundle-password", "wrong"])
    assert result.exit_code != 0


def test_peek_lists_keys(store_file):
    set_env(store_file, "pw", "proj", "ALPHA", "1")
    set_env(store_file, "pw", "proj", "BETA", "2")
    bundle = export_bundle(store_file, "pw", "proj", "bpw")
    result = _invoke(store_file, ["peek", bundle, "--bundle-password", "bpw"])
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output


def test_import_values_accessible_after_import(store_file):
    """Verify that imported variables can be retrieved from the destination project."""
    set_env(store_file, "pw", "src", "SECRET", "s3cr3t")
    bundle = export_bundle(store_file, "pw", "src", "bpw")
    result = _invoke(store_file, ["import", "dest", bundle, "--store", str(store_file),
                                   "--password", "pw", "--bundle-password", "bpw"])
    assert result.exit_code == 0
    assert get_env(store_file, "pw", "dest", "SECRET") == "s3cr3t"
