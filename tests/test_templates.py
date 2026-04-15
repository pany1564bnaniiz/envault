"""Tests for envault.templates module."""

from __future__ import annotations

import pytest

from envault.templates import (
    save_template,
    load_template,
    list_templates,
    delete_template,
    apply_template,
)
from envault.projects import get_env, get_all_env


@pytest.fixture()
def tmp_store(tmp_path):
    return str(tmp_path / "store.enc")


PASSWORD = "test-pass"


def test_save_and_load_template(tmp_store):
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    save_template(tmp_store, PASSWORD, "db-defaults", env)
    result = load_template(tmp_store, PASSWORD, "db-defaults")
    assert result == env


def test_load_template_missing_raises(tmp_store):
    with pytest.raises(KeyError, match="not found"):
        load_template(tmp_store, PASSWORD, "nonexistent")


def test_list_templates_empty(tmp_store):
    assert list_templates(tmp_store, PASSWORD) == []


def test_list_templates_sorted(tmp_store):
    save_template(tmp_store, PASSWORD, "zebra", {"A": "1"})
    save_template(tmp_store, PASSWORD, "alpha", {"B": "2"})
    assert list_templates(tmp_store, PASSWORD) == ["alpha", "zebra"]


def test_delete_template(tmp_store):
    save_template(tmp_store, PASSWORD, "to-delete", {"X": "1"})
    delete_template(tmp_store, PASSWORD, "to-delete")
    assert "to-delete" not in list_templates(tmp_store, PASSWORD)


def test_delete_template_missing_raises(tmp_store):
    with pytest.raises(KeyError, match="not found"):
        delete_template(tmp_store, PASSWORD, "ghost")


def test_apply_template_to_new_project(tmp_store):
    env = {"APP_ENV": "production", "LOG_LEVEL": "info"}
    save_template(tmp_store, PASSWORD, "app-defaults", env)
    written = apply_template(tmp_store, PASSWORD, "app-defaults", "myapp")
    assert set(written) == {"APP_ENV", "LOG_LEVEL"}
    assert get_env(tmp_store, PASSWORD, "myapp", "APP_ENV") == "production"


def test_apply_template_no_overwrite_by_default(tmp_store):
    from envault.projects import set_env
    set_env(tmp_store, PASSWORD, "proj", "KEY", "original")
    save_template(tmp_store, PASSWORD, "tmpl", {"KEY": "new-value", "OTHER": "x"})
    written = apply_template(tmp_store, PASSWORD, "tmpl", "proj", overwrite=False)
    assert "KEY" not in written
    assert get_env(tmp_store, PASSWORD, "proj", "KEY") == "original"


def test_apply_template_with_overwrite(tmp_store):
    from envault.projects import set_env
    set_env(tmp_store, PASSWORD, "proj", "KEY", "original")
    save_template(tmp_store, PASSWORD, "tmpl", {"KEY": "new-value"})
    apply_template(tmp_store, PASSWORD, "tmpl", "proj", overwrite=True)
    assert get_env(tmp_store, PASSWORD, "proj", "KEY") == "new-value"


def test_save_template_is_isolated_from_projects(tmp_store):
    save_template(tmp_store, PASSWORD, "mytmpl", {"FOO": "bar"})
    from envault.storage import list_projects
    assert "__templates__" not in list_projects(tmp_store, PASSWORD)
