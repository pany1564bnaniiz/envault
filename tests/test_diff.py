"""Tests for envault.diff module."""

import pytest

from envault.diff import DiffEntry, diff_envs, format_diff


def test_diff_added_key():
    old = {"A": "1"}
    new = {"A": "1", "B": "2"}
    entries = diff_envs(old, new)
    assert any(e.key == "B" and e.status == "added" for e in entries)


def test_diff_removed_key():
    old = {"A": "1", "B": "2"}
    new = {"A": "1"}
    entries = diff_envs(old, new)
    assert any(e.key == "B" and e.status == "removed" for e in entries)


def test_diff_changed_key():
    old = {"A": "1"}
    new = {"A": "99"}
    entries = diff_envs(old, new)
    assert len(entries) == 1
    assert entries[0].status == "changed"
    assert entries[0].old_value == "1"
    assert entries[0].new_value == "99"


def test_diff_unchanged_excluded_by_default():
    old = {"A": "1"}
    new = {"A": "1"}
    entries = diff_envs(old, new)
    assert entries == []


def test_diff_unchanged_included_when_requested():
    old = {"A": "1"}
    new = {"A": "1"}
    entries = diff_envs(old, new, show_unchanged=True)
    assert len(entries) == 1
    assert entries[0].status == "unchanged"


def test_diff_empty_dicts():
    assert diff_envs({}, {}) == []


def test_format_diff_no_entries():
    assert format_diff([]) == "No differences found."


def test_format_diff_masks_values_by_default():
    entries = [
        DiffEntry(key="SECRET", status="added", new_value="s3cr3t"),
    ]
    output = format_diff(entries, mask_values=True)
    assert "s3cr3t" not in output
    assert "***" in output


def test_format_diff_reveals_values_when_asked():
    entries = [
        DiffEntry(key="SECRET", status="added", new_value="s3cr3t"),
    ]
    output = format_diff(entries, mask_values=False)
    assert "s3cr3t" in output


def test_format_diff_prefixes():
    entries = [
        DiffEntry(key="A", status="added", new_value="1"),
        DiffEntry(key="B", status="removed", old_value="2"),
        DiffEntry(key="C", status="changed", old_value="3", new_value="4"),
    ]
    output = format_diff(entries, mask_values=False)
    assert "+ A" in output
    assert "- B" in output
    assert "~ C" in output
