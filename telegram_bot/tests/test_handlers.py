"""
Tests for telegram_bot handlers: error_handler and start_handler.
"""

import logging
from unittest.mock import AsyncMock, MagicMock

from aiogram.types import ErrorEvent

from core.entities import UserEntity
from telegram_bot.app_context import AppContext
from telegram_bot.handlers.errors import error_handler
from telegram_bot.handlers.start import start_handler


# ---------------------------------------------------------------------------
# Error handler tests
# ---------------------------------------------------------------------------

class TestErrorHandler:

    async def test_error_handler_logs_exception(self, caplog):
        exception = ValueError("test error")
        mock_event = MagicMock(spec=ErrorEvent)
        mock_event.exception = exception

        with caplog.at_level(logging.ERROR, logger="telegram_bot.handlers.errors"):
            await error_handler(event=mock_event)

        assert any("test error" in record.message for record in caplog.records)
        assert any(record.exc_info is not None for record in caplog.records)

    async def test_error_handler_logs_different_exception_types(self, caplog):
        exception = RuntimeError("runtime failure")
        mock_event = MagicMock(spec=ErrorEvent)
        mock_event.exception = exception

        with caplog.at_level(logging.ERROR, logger="telegram_bot.handlers.errors"):
            await error_handler(event=mock_event)

        assert any("runtime failure" in record.message for record in caplog.records)


# ---------------------------------------------------------------------------
# Start handler tests (fallback start handler)
# ---------------------------------------------------------------------------

class TestStartHandler:

    async def test_start_handler_sends_welcome_with_name(self):
        mock_message = AsyncMock()
        user = UserEntity(
            telegram_uid=12345,
            first_name="Alice",
            last_name="Smith",
        )

        mock_app_context = MagicMock(spec=AppContext)
        mock_app_context.send_message = AsyncMock()

        await start_handler(
            message=mock_message,
            user=user,
            app_context=mock_app_context,
        )

        mock_app_context.send_message.assert_called_once()
        call_text = mock_app_context.send_message.call_args[1]['text']
        assert "Alice Smith" in call_text
        assert "Welcome" in call_text

    async def test_start_handler_sends_welcome_first_name_only(self):
        mock_message = AsyncMock()
        user = UserEntity(
            telegram_uid=12345,
            first_name="Bob",
        )

        mock_app_context = MagicMock(spec=AppContext)
        mock_app_context.send_message = AsyncMock()

        await start_handler(
            message=mock_message,
            user=user,
            app_context=mock_app_context,
        )

        mock_app_context.send_message.assert_called_once()
        call_text = mock_app_context.send_message.call_args[1]['text']
        assert "Bob" in call_text
