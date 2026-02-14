"""
Helper functions for telegram bot
"""
from datetime import datetime
from typing import Any, Dict


def fix_unserializable_values_in_raw(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fix unserializable values in raw message data for JSON storage.

    Recursively converts datetime objects to ISO format strings.

    Args:
        raw: Raw message data dictionary

    Returns:
        Dictionary with all values JSON-serializable
    """
    if raw is None:
        return None

    fixed = {}
    for key, value in raw.items():
        if isinstance(value, datetime):
            fixed[key] = value.isoformat()
        elif isinstance(value, dict):
            fixed[key] = fix_unserializable_values_in_raw(value)
        elif isinstance(value, list):
            fixed[key] = [
                fix_unserializable_values_in_raw(item) if isinstance(item, dict)
                else item.isoformat() if isinstance(item, datetime)
                else item
                for item in value
            ]
        else:
            fixed[key] = value
    return fixed
