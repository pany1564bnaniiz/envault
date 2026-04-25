"""Tests for envault.workflows and envault.cli_workflows."""
from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envault.storage import save_store
from envault.workflows import (
    delete_workflow,
    list_workflows,
    load_workflow,
    save_workflow,
)
from envault.cli_workflows import cmd_workflow

PASSWORD = "wf-test-pass"


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "store.env")
    save_store(path, PASSWORD, {})
    return path


def _seed(store, name, steps=None):
    if steps is None:
        steps = [{"action": "set", "project": "p", "key": "K", "value": "V"}]
    save_workflow(store, PASSWORD, name, steps)


# --- unit tests ---

def test_save_and_load_workflow(tmp_store):
    steps = [{"action": "set", "project": "alpha", "key": "X", "value": "1"}]
    save_workflow(tmp_store, PASSWORD, "deploy", steps)
    loaded = load_workflow(tmp_store, PASSWORD, "deploy")
    assert loaded == steps


def test_list_workflows_empty(tmp_store):
    assert list_workflows(tmp_store, PASSWORD) == []


def test_list_workflows_sorted(tmp_store):
    _seed(tmp_store, "zebra")
    _seed(tmp_store, "alpha")
    assert list_workflows(tmp_store, PASSWORD) == ["alpha", "zebra"]


def test_load_workflow_missing_raises(tmp_store):
    with pytest.raises(KeyError, match="not found"):
        load_workflow(tmp_store, PASSWORD, "ghost")


def test_delete_workflow_removes_entry(tmp_store):
    _seed(tmp_store, "cleanup")
    delete_workflow(tmp_store, PASSWORD, "cleanup")
    assert "cleanup" not in list_workflows(tmp_store, PASSWORD)


def test_delete_workflow_missing_raises(tmp_store):
    with pytest.raises(KeyError):
        delete_workflow(tmp_store, PASSWORD, "nonexistent")


def test_save_workflow_invalid_action_raises(tmp_store):
    with pytest.raises(ValueError, match="Invalid workflow action"):
        save_workflow(tmp_store, PASSWORD, "bad", [{"action": "fly"}])


def test_save_workflow_empty_name_raises(tmp_store):
    with pytest.raises(ValueError, match="empty"):
        save_workflow(tmp_store, PASSWORD, "", [{"action": "set"}])


# --- CLI tests ---

def _invoke(args, store):
    runner = CliRunner()
    return runner.invoke(cmd_workflow, args + ["--store", store, "--password", PASSWORD])


def test_cli_save_success(tmp_store):
    steps = json.dumps([{"action": "set", "project": "p", "key": "K", "value": "V"}])
    result = _invoke(["save", "mywf", steps], tmp_store)
    assert result.exit_code == 0
    assert "saved" in result.output


def test_cli_list_shows_saved(tmp_store):
    _seed(tmp_store, "listwf")
    result = _invoke(["list"], tmp_store)
    assert "listwf" in result.output


def test_cli_list_empty_message(tmp_store):
    result = _invoke(["list"], tmp_store)
    assert "No workflows" in result.output


def test_cli_show_prints_json(tmp_store):
    steps = [{"action": "snapshot", "project": "beta", "label": "v1"}]
    save_workflow(tmp_store, PASSWORD, "snap", steps)
    result = _invoke(["show", "snap"], tmp_store)
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed == steps


def test_cli_delete_success(tmp_store):
    _seed(tmp_store, "todelete")
    result = _invoke(["delete", "todelete"], tmp_store)
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_cli_delete_missing_exits_nonzero(tmp_store):
    result = _invoke(["delete", "ghost"], tmp_store)
    assert result.exit_code != 0
