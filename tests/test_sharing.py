"""Tests for envault.sharing."""
import pytest
from pathlib import Path
from envault.sharing import export_bundle, import_bundle, list_bundle_keys
from envault.projects import set_env, get_env, get_all_env
from envault.storage import load_store
from cryptography.fernet import InvalidToken


@pytest.fixture()
def tmp_store(tmp_path):
    return tmp_path / "store"


def _seed(tmp_store, password, project, data):
    for k, v in data.items():
        set_env(tmp_store, password, project, k, v)


def test_export_returns_string(tmp_store):
    _seed(tmp_store, "pw", "proj", {"KEY": "val"})
    bundle = export_bundle(tmp_store, "pw", "proj", "bpw")
    assert isinstance(bundle, str)
    assert len(bundle) > 10


def test_export_import_roundtrip(tmp_store):
    _seed(tmp_store, "pw", "proj", {"A": "1", "B": "2"})
    bundle = export_bundle(tmp_store, "pw", "proj", "bpw")
    import_bundle(tmp_store, "pw", "dest", bundle, "bpw")
    assert get_env(tmp_store, "pw", "dest", "A") == "1"
    assert get_env(tmp_store, "pw", "dest", "B") == "2"


def test_import_creates_project_if_missing(tmp_store):
    _seed(tmp_store, "pw", "src", {"X": "42"})
    bundle = export_bundle(tmp_store, "pw", "src", "bpw")
    count = import_bundle(tmp_store, "pw", "newproj", bundle, "bpw")
    assert count == 1
    assert get_env(tmp_store, "pw", "newproj", "X") == "42"


def test_import_merges_existing_keys(tmp_store):
    _seed(tmp_store, "pw", "src", {"NEW": "n"})
    _seed(tmp_store, "pw", "dest", {"OLD": "o"})
    bundle = export_bundle(tmp_store, "pw", "src", "bpw")
    import_bundle(tmp_store, "pw", "dest", bundle, "bpw")
    assert get_env(tmp_store, "pw", "dest", "OLD") == "o"
    assert get_env(tmp_store, "pw", "dest", "NEW") == "n"


def test_wrong_bundle_password_raises(tmp_store):
    _seed(tmp_store, "pw", "proj", {"K": "v"})
    bundle = export_bundle(tmp_store, "pw", "proj", "correct")
    with pytest.raises(Exception):
        import_bundle(tmp_store, "pw", "dest", bundle, "wrong")


def test_list_bundle_keys(tmp_store):
    _seed(tmp_store, "pw", "proj", {"Z": "1", "A": "2"})
    bundle = export_bundle(tmp_store, "pw", "proj", "bpw")
    keys = list_bundle_keys(bundle, "bpw")
    assert keys == ["A", "Z"]


def test_list_bundle_keys_wrong_password_raises(tmp_store):
    _seed(tmp_store, "pw", "proj", {"K": "v"})
    bundle = export_bundle(tmp_store, "pw", "proj", "bpw")
    with pytest.raises(Exception):
        list_bundle_keys(bundle, "bad")
