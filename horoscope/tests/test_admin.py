"""Tests for admin command handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from horoscope.handlers.admin import refund_command_handler


def _make_user_entity(telegram_uid: int = 12345):
    user = MagicMock()
    user.telegram_uid = telegram_uid
    return user


class TestRefundCommand:

    @pytest.mark.asyncio
    async def test_non_admin_is_ignored(self):
        message = AsyncMock()
        message.text = "/refund charge_123"
        user = _make_user_entity(telegram_uid=99999)
        app_context = AsyncMock()

        with patch('horoscope.handlers.admin.settings') as mock_settings:
            mock_settings.ADMIN_USERS_IDS = [12345]

            await refund_command_handler(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_charge_id_shows_usage(self):
        message = AsyncMock()
        message.text = "/refund"
        user = _make_user_entity(telegram_uid=12345)
        app_context = AsyncMock()

        with patch('horoscope.handlers.admin.settings') as mock_settings:
            mock_settings.ADMIN_USERS_IDS = [12345]

            await refund_command_handler(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_called_once()
        assert "Usage" in app_context.send_message.call_args[1]['text']

    @pytest.mark.asyncio
    async def test_successful_refund(self):
        message = AsyncMock()
        message.text = "/refund charge_123"
        message.from_user.id = 12345
        user = _make_user_entity(telegram_uid=12345)
        app_context = AsyncMock()

        with patch('horoscope.handlers.admin.settings') as mock_settings:
            mock_settings.ADMIN_USERS_IDS = [12345]

            await refund_command_handler(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.bot.refund_star_payment.assert_called_once_with(
            user_id=12345,
            telegram_payment_charge_id="charge_123",
        )
        app_context.send_message.assert_called_once()
        assert "successful" in app_context.send_message.call_args[1]['text']

    @pytest.mark.asyncio
    async def test_refund_api_failure(self):
        message = AsyncMock()
        message.text = "/refund charge_123"
        message.from_user.id = 12345
        user = _make_user_entity(telegram_uid=12345)
        app_context = AsyncMock()
        app_context.bot.refund_star_payment = AsyncMock(
            side_effect=Exception("Telegram API error"),
        )

        with patch('horoscope.handlers.admin.settings') as mock_settings:
            mock_settings.ADMIN_USERS_IDS = [12345]

            await refund_command_handler(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_called_once()
        assert "failed" in app_context.send_message.call_args[1]['text'].lower()
