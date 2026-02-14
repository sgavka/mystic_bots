"""Tests for telegram_bot.helpers module."""

from datetime import datetime

from telegram_bot.helpers import fix_unserializable_values_in_raw


class TestFixUnserializableValuesInRaw:

    def test_none_input(self):
        assert fix_unserializable_values_in_raw(None) is None

    def test_empty_dict(self):
        assert fix_unserializable_values_in_raw({}) == {}

    def test_simple_values_unchanged(self):
        raw = {"text": "hello", "id": 123, "active": True}
        result = fix_unserializable_values_in_raw(raw)
        assert result == raw

    def test_datetime_converted_to_isoformat(self):
        dt = datetime(2025, 1, 15, 10, 30, 0)
        raw = {"created_at": dt, "text": "hello"}
        result = fix_unserializable_values_in_raw(raw)
        assert result["created_at"] == "2025-01-15T10:30:00"
        assert result["text"] == "hello"

    def test_nested_dict_datetime(self):
        dt = datetime(2025, 6, 1, 12, 0, 0)
        raw = {"chat": {"created_at": dt, "id": 1}}
        result = fix_unserializable_values_in_raw(raw)
        assert result["chat"]["created_at"] == "2025-06-01T12:00:00"
        assert result["chat"]["id"] == 1

    def test_list_with_dicts(self):
        dt = datetime(2025, 3, 10, 8, 0, 0)
        raw = {"items": [{"date": dt}, {"name": "test"}]}
        result = fix_unserializable_values_in_raw(raw)
        assert result["items"][0]["date"] == "2025-03-10T08:00:00"
        assert result["items"][1]["name"] == "test"

    def test_list_with_datetime(self):
        dt = datetime(2025, 2, 20, 15, 45, 0)
        raw = {"dates": [dt, "text", 42]}
        result = fix_unserializable_values_in_raw(raw)
        assert result["dates"][0] == "2025-02-20T15:45:00"
        assert result["dates"][1] == "text"
        assert result["dates"][2] == 42

    def test_deeply_nested(self):
        dt = datetime(2025, 1, 1)
        raw = {"a": {"b": {"c": {"timestamp": dt}}}}
        result = fix_unserializable_values_in_raw(raw)
        assert result["a"]["b"]["c"]["timestamp"] == "2025-01-01T00:00:00"

    def test_none_values_in_dict(self):
        raw = {"text": None, "id": 1}
        result = fix_unserializable_values_in_raw(raw)
        assert result["text"] is None
        assert result["id"] == 1
