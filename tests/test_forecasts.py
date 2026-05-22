"""Tests for envault.forecasts."""
import pytest

from envault.forecasts import (
    clear_forecasts,
    get_forecasts,
    latest_forecast,
    record_forecast,
)
from envault.storage import save_store


@pytest.fixture()
def tmp_store(tmp_path):
    path = str(tmp_path / "vault.enc")
    return path


def _seed(store_path, password="pw"):
    save_store(store_path, password, {"myproject": {"KEY": "val"}})


def test_record_forecast_returns_entry(tmp_store):
    _seed(tmp_store)
    entry = record_forecast(tmp_store, "pw", "myproject", 30, 5, 0.8)
    assert entry["project"] == "myproject"
    assert entry["horizon_days"] == 30
    assert entry["predicted_changes"] == 5
    assert entry["confidence"] == 0.8
    assert "created_at" in entry


def test_record_forecast_persists(tmp_store):
    _seed(tmp_store)
    record_forecast(tmp_store, "pw", "myproject", 14, 3, 0.75, notes="Q1")
    entries = get_forecasts(tmp_store, "pw", "myproject")
    assert len(entries) == 1
    assert entries[0]["notes"] == "Q1"


def test_record_multiple_forecasts(tmp_store):
    _seed(tmp_store)
    record_forecast(tmp_store, "pw", "myproject", 7, 1, 0.5)
    record_forecast(tmp_store, "pw", "myproject", 30, 10, 0.9)
    entries = get_forecasts(tmp_store, "pw", "myproject")
    assert len(entries) == 2


def test_get_forecasts_newest_first(tmp_store):
    _seed(tmp_store)
    record_forecast(tmp_store, "pw", "myproject", 7, 1, 0.5)
    record_forecast(tmp_store, "pw", "myproject", 30, 10, 0.9)
    entries = get_forecasts(tmp_store, "pw", "myproject")
    assert entries[0]["horizon_days"] == 30


def test_get_forecasts_empty_when_none(tmp_store):
    _seed(tmp_store)
    assert get_forecasts(tmp_store, "pw", "myproject") == []


def test_latest_forecast_returns_most_recent(tmp_store):
    _seed(tmp_store)
    record_forecast(tmp_store, "pw", "myproject", 7, 2, 0.6)
    record_forecast(tmp_store, "pw", "myproject", 90, 20, 0.95)
    latest = latest_forecast(tmp_store, "pw", "myproject")
    assert latest["horizon_days"] == 90


def test_latest_forecast_returns_none_when_empty(tmp_store):
    _seed(tmp_store)
    assert latest_forecast(tmp_store, "pw", "myproject") is None


def test_record_forecast_missing_project_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(KeyError):
        record_forecast(tmp_store, "pw", "ghost", 10, 1, 0.5)


def test_record_forecast_invalid_horizon_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="horizon_days"):
        record_forecast(tmp_store, "pw", "myproject", 0, 1, 0.5)


def test_record_forecast_invalid_confidence_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="confidence"):
        record_forecast(tmp_store, "pw", "myproject", 10, 1, 1.5)


def test_record_forecast_negative_changes_raises(tmp_store):
    _seed(tmp_store)
    with pytest.raises(ValueError, match="predicted_changes"):
        record_forecast(tmp_store, "pw", "myproject", 10, -3, 0.5)


def test_clear_forecasts_returns_count(tmp_store):
    _seed(tmp_store)
    record_forecast(tmp_store, "pw", "myproject", 7, 1, 0.5)
    record_forecast(tmp_store, "pw", "myproject", 14, 2, 0.7)
    removed = clear_forecasts(tmp_store, "pw", "myproject")
    assert removed == 2
    assert get_forecasts(tmp_store, "pw", "myproject") == []


def test_clear_forecasts_zero_when_none(tmp_store):
    _seed(tmp_store)
    assert clear_forecasts(tmp_store, "pw", "myproject") == 0
