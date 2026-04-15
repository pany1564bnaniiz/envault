"""Tests for envault.export module."""

import os
from pathlib import Path

import pytest

from envault.export import export_env, import_env
from envault.projects import get_all_env, get_env
from envault.storage import save_store

PASSWORD = "test-secret"


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    store_file = tmp_path / "store.json.enc"
    monkeypatch.setattr("envault.storage._store_path", lambda: store_file)
    save_store({}, PASSWORD)
    return store_file


def _seed_project(project: str, vars: dict) -> None:
    from envault.projects import set_env
    for k, v in vars.items():
        set_env(project, k, v, PASSWORD)


# ---------------------------------------------------------------------------
# export_env
# ---------------------------------------------------------------------------

def test_export_returns_dotenv_format():
    _seed_project("myapp", {"DB_HOST": "localhost", "PORT": "5432"})
    content = export_env("myapp", PASSWORD)
    assert "DB_HOST=localhost" in content
    assert "PORT=5432" in content


def test_export_writes_file(tmp_path):
    _seed_project("myapp", {"KEY": "value"})
    out = tmp_path / ".env"
    export_env("myapp", PASSWORD, output_path=str(out))
    assert out.exists()
    assert "KEY=value" in out.read_text()


def test_export_file_permissions(tmp_path):
    _seed_project("myapp", {"SECRET": "abc"})
    out = tmp_path / ".env"
    export_env("myapp", PASSWORD, output_path=str(out))
    mode = oct(os.stat(out).st_mode)[-3:]
    assert mode == "600"


def test_export_quotes_values_with_spaces():
    _seed_project("myapp", {"GREETING": "hello world"})
    content = export_env("myapp", PASSWORD)
    assert 'GREETING="hello world"' in content


def test_export_missing_project_raises():
    with pytest.raises(KeyError):
        export_env("nonexistent", PASSWORD)


# ---------------------------------------------------------------------------
# import_env
# ---------------------------------------------------------------------------

def test_import_reads_dotenv_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=abc123\nDEBUG=true\n")
    count = import_env("newproject", PASSWORD, input_path=str(env_file))
    assert count == 2
    assert get_env("newproject", "API_KEY", PASSWORD) == "abc123"
    assert get_env("newproject", "DEBUG", PASSWORD) == "true"


def test_import_skips_comments_and_blank_lines(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\n\nFOO=bar\n")
    count = import_env("proj", PASSWORD, input_path=str(env_file))
    assert count == 1


def test_import_strips_quotes(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('MSG="hello world"\n')
    import_env("proj", PASSWORD, input_path=str(env_file))
    assert get_env("proj", "MSG", PASSWORD) == "hello world"


def test_import_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        import_env("proj", PASSWORD, input_path="/no/such/file.env")


def test_import_malformed_line_raises(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("BADLINE\n")
    with pytest.raises(ValueError, match="Malformed"):
        import_env("proj", PASSWORD, input_path=str(env_file))


def test_roundtrip_export_import(tmp_path):
    original = {"HOST": "db.local", "PORT": "3306", "NAME": "mydb"}
    _seed_project("source", original)
    out = tmp_path / ".env"
    export_env("source", PASSWORD, output_path=str(out))
    import_env("destination", PASSWORD, input_path=str(out))
    result = get_all_env("destination", PASSWORD)
    assert result == original
