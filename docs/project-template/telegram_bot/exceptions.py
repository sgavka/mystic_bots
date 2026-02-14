"""
Custom exceptions for telegram_bot app.
"""


class MessageHistoryNotFoundException(Exception):
    """Raised when a MessageHistory record is not found."""
    pass
