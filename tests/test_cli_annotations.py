"""Tests for envault.cli_annotations."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_annotations import cmd_annotation
from envault.projects import set_env
from envault.storage import save_store


@pytest.fixture()
def store_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_store(path, "pw", {})
    set_env(path, "pw", "myapp", "API_KEY", "secret")
    return path


def _invoke(store_file, *args):
    runner = CliRunner()
    base = ["--store", store_file, "--password", "pw"]
    return runner.invoke(cmd_annotation, list(args) + base)


def test_annotation_set_success(store_file):
    result = _invoke(store_file, "set", "myapp", "API_KEY", "The API key")
    assert result.exit_code == 0
    assert "Annotation set" in result.output


def test_annotation_get_shows_note(store_file):
    _invoke(store_file, "set", "myapp", "API_KEY", "The API key")
    result = _invoke(store_file, "get", "myapp", "API_KEY")
    assert result.exit_code == 0
    assert "The API key" in result.output


def test_annotation_get_unset_key(store_file):
    result = _invoke(store_file, "get", "myapp", "API_KEY")
    assert result.exit_code == 0
    assert "No annotation" in result.output


def test_annotation_delete_success(store_file):
    _invoke(store_file, "set", "myapp", "API_KEY", "note")
    result = _invoke(store_file, "delete", "myapp", "API_KEY")
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_annotation_delete_absent(store_file):
    result = _invoke(store_file, "delete", "myapp", "API_KEY")
    assert result.exit_code == 0
    assert "No annotation found" in result.output


def test_annotation_list_empty(store_file):
    result = _invoke(store_file, "list", "myapp")
    assert result.exit_code == 0
    assert "No annotations" in result.output


def test_annotation_list_shows_entries(store_file):
    _invoke(store_file, "set", "myapp", "API_KEY", "key note")
    result = _invoke(store_file, "list", "myapp")
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "key note" in result.output


def test_annotation_set_missing_key_exits_nonzero(store_file):
    result = _invoke(store_file, "set", "myapp", "DOES_NOT_EXIST", "note")
    assert result.exit_code != 0
