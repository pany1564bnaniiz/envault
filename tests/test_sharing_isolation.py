"""Ensure sharing bundles don't leak internal metadata keys."""
import pytest
from pathlib import Path
from envault.projects import set_env
from envault.tags import add_tag
from envault.notes import set_note
from envault.sharing import export_bundle, list_bundle_keys


@pytest.fixture()
def seeded_store(tmp_path):
    store = tmp_path / "store"
    set_env(store, "pw", "proj", "REAL_KEY", "real_value")
    add_tag(store, "pw", "proj", "mytag")
    set_note(store, "pw", "proj", "A note")
    return store


def test_bundle_contains_real_key(seeded_store):
    keys = list_bundle_keys(
        export_bundle(seeded_store, "pw", "proj", "bpw"), "bpw"
    )
    assert "REAL_KEY" in keys


def test_bundle_excludes_tags_key(seeded_store):
    keys = list_bundle_keys(
        export_bundle(seeded_store, "pw", "proj", "bpw"), "bpw"
    )
    assert "__tags__" not in keys


def test_bundle_excludes_notes_key(seeded_store):
    keys = list_bundle_keys(
        export_bundle(seeded_store, "pw", "proj", "bpw"), "bpw"
    )
    assert "__note__" not in keys


def test_roundtrip_does_not_import_metadata(seeded_store, tmp_path):
    dest_store = tmp_path / "dest_store"
    set_env(dest_store, "pw", "dest", "PLACEHOLDER", "x")
    bundle = export_bundle(seeded_store, "pw", "proj", "bpw")
    from envault.sharing import import_bundle
    from envault.storage import load_store
    import_bundle(dest_store, "pw", "dest", bundle, "bpw")
    store = load_store(dest_store, "pw")
    assert "__tags__" not in store.get("dest", {})
    assert "__note__" not in store.get("dest", {})
